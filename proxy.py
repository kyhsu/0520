import sys
import os
import socket
import signal
import shlex
import pexpect

SOCKET_PATH = '/tmp/proxy_socket'


def main():
    if len(sys.argv) < 2:
        print("Usage: proxy.py '<command>'")
        sys.exit(1)

    command = sys.argv[1]
    args = shlex.split(command)

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    child = pexpect.spawn(args[0], args[1:], encoding='utf-8', echo=False)

    # wait for initial prompt
    try:
        child.expect('> ')
    except pexpect.EOF:
        print('Process exited unexpectedly')
        sys.exit(1)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    sock.listen(1)

    def cleanup(signum=None, frame=None):
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass
        child.close(force=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        conn, _ = sock.accept()
        with conn:
            data = b''
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
            command = data.decode().strip()
            if not command:
                continue
            child.sendline(command)
            child.expect('> ')
            response = child.before
            conn.sendall(response.encode())


if __name__ == '__main__':
    main()
