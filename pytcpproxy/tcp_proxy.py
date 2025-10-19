import argparse
import socket
import threading


class TCPProxy:
    def __init__(self, local_host, local_port, remote_host, remote_port):
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.connection_count = 0
        self.connection_lock = threading.Lock()
        self.running = False
        self.server_socket = None

    def run(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.local_host, self.local_port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)
        print(f"[*] Listening on {self.local_host}:{self.local_port}")
        print(f"[*] Forwarding traffic to {self.remote_host}:{self.remote_port}")

        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

                with self.connection_lock:
                    self.connection_count += 1
                    print(f"[*] Current connections: {self.connection_count}")

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,),
                )
                thread.start()
            except socket.timeout:
                continue
            except OSError:
                break

    def handle_client(self, client_socket):
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_socket.connect((self.remote_host, self.remote_port))
        except Exception as e:
            print(
                f"[*] Failed to connect to {self.remote_host}:{self.remote_port}: {e}"
            )
            client_socket.close()
            self.decrement_connection_count()
            return

        client_socket.settimeout(60)
        remote_socket.settimeout(60)

        t1 = threading.Thread(target=self.forward, args=(client_socket, remote_socket))
        t2 = threading.Thread(target=self.forward, args=(remote_socket, client_socket))
        t1.start()
        t2.start()

        t1.join()
        t2.join()

        client_socket.close()
        remote_socket.close()

        self.decrement_connection_count()

    def forward(self, src, dst):
        try:
            while True:
                try:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
                except socket.timeout:
                    break
        except OSError as e:
            print(f"[*] OSError in forward: {e}")
        finally:
            try:
                src.shutdown(socket.SHUT_RD)
                dst.shutdown(socket.SHUT_WR)
            except OSError as e:
                if e.errno != 107:
                    print(f"[*] OSError on shutdown: {e}")

    def decrement_connection_count(self):
        with self.connection_lock:
            self.connection_count -= 1
            print(
                f"[*] Connection closed. Current connections: {self.connection_count}"
            )

    def shutdown(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()


def main():
    parser = argparse.ArgumentParser(description="A simple TCP proxy.")
    parser.add_argument("remote_host", help="The remote host to forward traffic to.")
    parser.add_argument(
        "remote_port", type=int, help="The remote port to forward traffic to."
    )
    parser.add_argument(
        "--local-host",
        default="0.0.0.0",
        help="The local host to listen on.",
    )
    parser.add_argument(
        "--local-port",
        type=int,
        default=8000,
        help="The local port to listen on.",
    )
    args = parser.parse_args()

    proxy = TCPProxy(
        args.local_host,
        args.local_port,
        args.remote_host,
        args.remote_port,
    )
    try:
        proxy.run()
    except KeyboardInterrupt:
        proxy.shutdown()


if __name__ == "__main__":
    main()
