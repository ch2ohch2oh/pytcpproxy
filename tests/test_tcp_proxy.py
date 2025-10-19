import socket
import sys
import threading
import time

import pytest

from pytcpproxy.tcp_proxy import main as proxy_main


@pytest.fixture
def echo_server():
    def handle_echo(client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.sendall(data)
        client_socket.close()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 12345))
    server.listen(1)
    server_thread = threading.Thread(target=lambda: handle_echo(server.accept()[0]))
    server_thread.daemon = True
    server_thread.start()
    yield
    server.close()


@pytest.fixture
def proxy_server():
    original_argv = sys.argv
    sys.argv = ["pytcpproxy", "localhost", "12345"]
    proxy_thread = threading.Thread(target=proxy_main)
    proxy_thread.daemon = True
    proxy_thread.start()
    time.sleep(1)  # Give the proxy server time to start
    yield
    sys.argv = original_argv


def test_tcp_proxy(echo_server, proxy_server):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 8000))
    client_socket.sendall(b"hello world")
    response = client_socket.recv(1024)
    client_socket.close()
    assert response == b"hello world"
