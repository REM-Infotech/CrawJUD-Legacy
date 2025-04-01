"""Module to handle sending messages via SocketIo.

Classes:
    SendMessage: Handle sending messages via SocketIo.

"""

import asyncio
from typing import Self

from dotenv_vault import load_dotenv
from socketio import AsyncSimpleClient

from crawjud.bot.core import CrawJUD

load_dotenv()


class SendMessage(CrawJUD):
    """Handle sending messages via SocketIo.

    Functions:
        setup_message: Set up the message to be sent by the bot.
        socket_message: Emit log message to the socket with termination checks.
        badnamespace: Handle bad namespace error when emitting an event.
        connectionerror: Handle connection error when emitting an event.
        connect_socket: Connect to the socket server using the specified URL and headers.

    """

    def __init__(self) -> None:
        """Initialize the SendMessage class."""

    def setup_message(self, status_bot: str = "Em Execução") -> None:
        """Set up the message to be sent by the bot."""
        data = {
            "message": self.prompt,
            "pid": self.pid,
            "type": self.type_log,
            "pos": self.row,
            "graphicMode": self.graphicMode,
            "total": self.total_rows,
            "status": status_bot,
            "schedule": self.schedule,
        }

        if status_bot != "Em Execução":
            asyncio.run(self.socket_message(data, "stop_bot"))

        asyncio.run(self.socket_message(data))

    async def socket_message(self: Self, data: dict, event: str = "log_message") -> None:
        """Emit log message to the socket with termination checks.

        Updates data with system info if termination patterns are detected and
        sends the message through the socket.

        Args:
            data (dict): Dictionary containing log details.
            event (str, optional): The event to emit. Defaults to "log_message".

        """
        async with AsyncSimpleClient() as sio:
            await sio.connect(url="https://api.reminfotech.net.br", namespace="/log", headers={"pid": self.pid})
            await sio.emit(event, data)
