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
from select import select
from sys import stdin
from queue import Queue

from docopt import docopt


def chat():
    arguments = docopt(__doc__)
    _validate_arguments(arguments['<remote-host>'], arguments['<local-port>'], arguments['<remote-port>'])
    sock = _connect_to_peer(arguments['<remote-host>'], int(arguments['<local-port>']), int(arguments['<remote-port>']))

    inputs = [sock, stdin]
    outputs = [sock]

    outgoing_messages = Queue(maxsize=100)

    readable, writable, exceptional = select(inputs, outputs, inputs)
    while True:
        for s in readable:
            if s == sock:
                incoming_message = s.recv(2048)
                if incoming_message:
                    print(incoming_message)
                else:
                    sock.close()
                    break
            else:
                user_input = s.readline()
                outgoing_messages.put(user_input)

        for s in writable:
            if not Queue.empty():
                s.send(outgoing_messages.get(block=False))

        for s in exceptional:
            if s == sock:
                sock.close()
                break


def _connect_to_peer(remote_host: str, local_port: int, remote_port: int):
    sock = _connect_as_client(remote_host, remote_port)
    if not sock:
        sock = _connect_as_server(remote_host, local_port)
    return sock


def _connect_as_client(remote_host: str, remote_port: int):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((remote_host, remote_port))
    except ConnectionRefusedError:
        return None

    print(f"Connected as client to: {remote_host}:{remote_port}")
    return s


def _connect_as_server(remote_host: str, local_port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((remote_host, local_port))
        s.listen()
        conn, addr = s.accept()

    print(f"Connected as server to: {addr[0]}:{addr[1]}")
    return conn


def _validate_arguments(remote_host: str, local_port: str, remote_port: str):
    if not 0 < int(local_port) < 65536 or not 0 < int(remote_port) < 65536:
        raise ValueError("Illegal port number")
    socket.inet_aton(remote_host)


if __name__ == '__main__':
    chat()