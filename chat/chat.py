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

from docopt import docopt
from aioconsole import ainput


def chat():
    arguments = docopt(__doc__)
    _validate_arguments(arguments['<remote-host>'], arguments['<local-port>'], arguments['<remote-port>'])

    loop = asyncio.get_event_loop()
    receive_task = asyncio.Task(asyncio.start_server(_handle_session_receive_task, arguments['<remote-host>'],
                                                     int(arguments['<local-port>'])))
    transmit_task = asyncio.Task(_handle_session_transmit_task(arguments['<remote-host>'],
                                                               int(arguments['<remote-port>']),
                                                               arguments['--username']))
    loop.run_forever()


def _validate_arguments(remote_host: str, local_port: str, remote_port: str):
    if not 0 < int(local_port) < 65536 or not 0 < int(remote_port) < 65536:
        raise ValueError("Illegal port number")
    socket.inet_aton(remote_host)


async def _handle_session_receive_task(reader, _):
    while True:
        try:
            incoming_message = await reader.read(2048)
            print(incoming_message.decode())
        except ConnectionResetError as e:
            raise e


async def _handle_session_transmit_task(remote_host: str, remote_port: int, username: str):
    while True:
        try:
            _, writer = await asyncio.open_connection(remote_host, remote_port)
            break
        except ConnectionRefusedError:
            pass

    while True:
        try:
            outgoing_message = f'{username}: {await ainput()}'
            writer.write(outgoing_message.encode())
        except Exception as e:
            writer.close()
            print(e)


if __name__ == '__main__':
    chat()

