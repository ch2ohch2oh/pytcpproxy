import socket
import threading


def handle_client(client_socket, remote_host, remote_port):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
    except Exception as e:
        print(f"[*] Failed to connect to {remote_host}:{remote_port}: {e}")
        client_socket.close()
        return

    def forward(src, dst):
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
        src.close()
        dst.close()

    threading.Thread(target=forward, args=(client_socket, remote_socket)).start()
    threading.Thread(target=forward, args=(remote_socket, client_socket)).start()


def main():
    local_host = "0.0.0.0"
    local_port = 8000
    remote_host = "localhost"  # Replace with your target host
    remote_port = 12345  # Replace with your target port

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)
    print(f"[*] Listening on {local_host}:{local_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        thread = threading.Thread(
            target=handle_client, args=(client_socket, remote_host, remote_port)
        )
        thread.start()


if __name__ == "__main__":
    main()
