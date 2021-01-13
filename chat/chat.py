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
import asyncio
import asyncio_dgram

from docopt import docopt
from aioconsole import ainput


def chat():
    arguments = docopt(__doc__)
    _validate_arguments(arguments['<remote-host>'], arguments['<local-port>'], arguments['<remote-port>'])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(_handle_session_receive_task((arguments['<remote-host>'],
                                                                         arguments['<local-port>'])),
                                           _handle_session_transmit_task((arguments['<remote-host>'],
                                                                          arguments['<remote-port>']),
                                                                         arguments['--username'])))


def _validate_arguments(remote_host: str, local_port: str, remote_port: str):
    try:
        if not 0 < int(local_port) < 65536 or not 0 < int(remote_port) < 65536:
            raise ValueError("Illegal port number")
        socket.inet_aton(remote_host)
    except ValueError as e:
        raise e
    except socket.error as e:
        raise e


async def _handle_session_receive_task(local_host: tuple):
    stream = await asyncio_dgram.bind(local_host)
    while True:
        incoming_message, _ = await stream.recv()
        print(incoming_message.decode())


async def _handle_session_transmit_task(remote_host: tuple, username: str):
    stream = await asyncio_dgram.connect(remote_host)
    while True:
        try:
            outgoing_message = (username + ": ").encode() + (await ainput()).encode()
            await stream.send(outgoing_message)
        except OSError:
            print("Message wasn't sent successfully")
            stream.close()
            stream = await asyncio_dgram.connect(remote_host)


if __name__ == '__main__':
    chat()

