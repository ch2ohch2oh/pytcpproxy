import socket
import threading
import time

import pytest

from pytcpproxy.tcp_proxy import TCPProxy


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def echo_server():
    port = get_free_port()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen(1)
    server_socket.settimeout(1)

    def handle_client(client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                client_socket.sendall(data)
        finally:
            client_socket.close()

    def run_server():
        while True:
            try:
                client_socket, _ = server_socket.accept()
                threading.Thread(target=handle_client, args=(client_socket,)).start()
            except OSError:
                break

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    yield "localhost", port

    server_socket.close()
    server_thread.join()


@pytest.fixture
def proxy_server(echo_server):
    remote_host, remote_port = echo_server
    local_port = get_free_port()
    proxy = TCPProxy("localhost", local_port, remote_host, remote_port)

    proxy_thread = threading.Thread(target=proxy.run)
    proxy_thread.start()

    # Wait for the proxy to be ready
    for _ in range(10):
        try:
            with socket.create_connection(("localhost", local_port), timeout=0.1):
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    else:
        pytest.fail("Proxy server did not start in time")

    time.sleep(0.1)

    yield proxy

    proxy.shutdown()
    proxy_thread.join()


def test_tcp_proxy(proxy_server):
    proxy_host, proxy_port = proxy_server.local_host, proxy_server.local_port
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((proxy_host, proxy_port))
        client_socket.sendall(b"hello world")
        response = client_socket.recv(1024)
        assert response == b"hello world"
    finally:
        client_socket.close()


def test_connection_count(proxy_server):
    assert proxy_server.connection_count == 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((proxy_server.local_host, proxy_server.local_port))
        time.sleep(0.1)
        assert proxy_server.connection_count == 1
    finally:
        client_socket.close()

    time.sleep(0.1)
    assert proxy_server.connection_count == 0


def test_multiple_connections(proxy_server):
    assert proxy_server.connection_count == 0

    sockets = []
    for _ in range(5):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((proxy_server.local_host, proxy_server.local_port))
        sockets.append(client_socket)

    time.sleep(0.1)
    assert proxy_server.connection_count == 5

    for client_socket in sockets:
        client_socket.close()

    time.sleep(0.1)
    assert proxy_server.connection_count == 0
