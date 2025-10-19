import argparse
import socket
import threading

connection_count = 0
connection_lock = threading.Lock()


def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except OSError as e:
        print(f"[*] OSError in forward: {e}")
    finally:
        try:
            src.shutdown(socket.SHUT_RD)
            dst.shutdown(socket.SHUT_WR)
        except OSError as e:
            print(f"[*] OSError on shutdown: {e}")


def handle_client(client_socket, remote_host, remote_port):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
    except Exception as e:
        print(f"[*] Failed to connect to {remote_host}:{remote_port}: {e}")
        client_socket.close()
        decrement_connection_count()
        return

    t1 = threading.Thread(target=forward, args=(client_socket, remote_socket))
    t2 = threading.Thread(target=forward, args=(remote_socket, client_socket))
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    client_socket.close()
    remote_socket.close()

    decrement_connection_count()


def decrement_connection_count():
    with connection_lock:
        global connection_count
        connection_count -= 1
        print(f"[*] Connection closed. Current connections: {connection_count}")


def main():
    parser = argparse.ArgumentParser(description="A simple TCP proxy.")
    parser.add_argument("remote_host", help="The remote host to forward traffic to.")
    parser.add_argument(
        "remote_port", type=int, help="The remote port to forward traffic to."
    )
    parser.add_argument(
        "--local-host", default="0.0.0.0", help="The local host to listen on."
    )
    parser.add_argument(
        "--local-port", type=int, default=8000, help="The local port to listen on."
    )
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((args.local_host, args.local_port))
    server.listen(5)
    print(f"[*] Listening on {args.local_host}:{args.local_port}")
    print(f"[*] Forwarding traffic to {args.remote_host}:{args.remote_port}")

    global connection_count
    connection_count = 0

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

        with connection_lock:
            connection_count += 1
            print(f"[*] Current connections: {connection_count}")

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, args.remote_host, args.remote_port),
        )
        thread.start()


if __name__ == "__main__":
    main()
