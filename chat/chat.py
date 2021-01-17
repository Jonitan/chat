"""
Run the chat against another endpoint.

Usage:
    chat.py <local-port> <remote-host> <remote-port> [--username <name>]
    chat.py (-h | --help)

Options:
    -u <name>, --username <name>    The user nickname [default: guest].
    -h, --help                      Show this message and exit.
"""
import socket
import threading
import select
from sys import stdin
from queue import Queue

from docopt import docopt

stop_session = False

def chat():
    arguments = docopt(__doc__)
    _validate_arguments(arguments['<remote-host>'], arguments['<local-port>'], arguments['<remote-port>'])

    outgoing_messages_queue = Queue(maxsize=100)

    sock = _connect_to_peer(arguments['<remote-host>'], int(arguments['<local-port>']), int(arguments['<remote-port>']))

    session_thread = threading.Thread(target=_handle_session, args=(sock, outgoing_messages_queue,
                                                                    arguments['--username']))
    user_input_thread = threading.Thread(target=_handle_user_input, args=(outgoing_messages_queue,))
    user_input_thread.daemon = True

    session_thread.start()
    user_input_thread.start()


def _handle_session(sock, outgoing_messages_queue: Queue, username: str):
    while True:
        readable, writable, exceptional = select.select([sock], [sock], [])

        if readable:
            if not _handle_session_read(sock):
                break

        if writable:
            if not _handle_session_write(sock, outgoing_messages_queue, username):
                break


def _handle_session_read(sock) -> bool:
    try:
        incoming_message = sock.recv(1024)
        if incoming_message:
            print(incoming_message.decode())
            return True
        else:
            return _shutdown_session(sock)
    except ConnectionResetError:
        return _shutdown_session(sock)


def _handle_session_write(sock, outgoing_messages_queue: Queue, username: str) -> bool:
    try:
        if not outgoing_messages_queue.empty():
            message = outgoing_messages_queue.get(block=False)
            sock.sendall(f'{username}: {message}'.encode())
        return True
    except ConnectionResetError:
        return _shutdown_session(sock)


def _handle_user_input(outgoing_messages_queue: Queue):
    while True:
        for line in stdin:
            if line:
                outgoing_messages_queue.put(line)


def _connect_to_peer(remote_host: str, local_port: int, remote_port: int):
    sock = _connect_as_client(remote_host, remote_port)
    if not sock:
        sock = _connect_as_server(remote_host, local_port)
    return sock


def _connect_as_client(remote_host: str, remote_port: int):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((remote_host, remote_port))
    except ConnectionRefusedError:
        return None

    print(f"Connected as client to: {remote_host}:{remote_port}")
    return sock


def _connect_as_server(remote_host: str, local_port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((remote_host, local_port))
    sock.listen()
    conn, addr = sock.accept()
    sock.close()

    print(f"Connected as server to: {addr[0]}:{addr[1]}")
    return conn


def _shutdown_session(sock) -> bool:
    print("Disconnected: Peer closed connection.")
    sock.close()
    return False


def _validate_arguments(remote_host: str, local_port: str, remote_port: str):
    if not 0 < int(local_port) < 65536 or not 0 < int(remote_port) < 65536:
        raise ValueError("Illegal port number")
    socket.inet_aton(remote_host)


if __name__ == '__main__':
    chat()