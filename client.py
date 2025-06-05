import sys
import socket

SOCKET_PATH = '/tmp/proxy_socket'


def main():
    if len(sys.argv) < 2:
        print("Usage: client.py '<command>'")
        sys.exit(1)

    command = sys.argv[1]

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)
    try:
        sock.sendall(command.encode())
        sock.shutdown(socket.SHUT_WR)
        data = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
        print(data.decode().rstrip())
    finally:
        sock.close()


if __name__ == '__main__':
    main()
