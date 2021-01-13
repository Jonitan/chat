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

from docopt import docopt


def chat():
    arguments = docopt(__doc__)
    _validate_arguments(arguments['<remote-host>'], arguments['<local-port>'], arguments['<remote-port>'])
    # TODO


def _validate_arguments(ip_address: str, local_port: str, remote_port: str):
    try:
        if not 0 < int(local_port) < 65536 or not 0 < int(remote_port) < 65536:
            raise ValueError("Illegal port number")
        socket.inet_aton(ip_address)
    except ValueError as e:
        raise e
    except socket.error as e:
        raise e


if __name__ == '__main__':
    chat()