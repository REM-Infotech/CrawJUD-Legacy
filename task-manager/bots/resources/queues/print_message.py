"""Sistema de envio de logs para o ClientUI."""

from contextlib import suppress
from datetime import datetime
from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING, TypedDict
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from socketio import Client

from app.interfaces import Message
from app.types import AnyType, MessageType
from config import config

if TYPE_CHECKING:
    from bots.head import CrawJUD

load_dotenv()


class Count(TypedDict):
    """Dicionario de contagem."""

    success_count: int = 0
    remainign_count: int = 0
    error_count: int = 0


class PrintMessage:
    """Envio de logs para o FrontEnd."""

    bot: CrawJUD
    _message_type: MessageType

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de sucessos."""
        self.bot = bot
        self.queue_print_bot = Queue()
        self.thread_print_bot = Thread(target=self.print_msg, daemon=True)
        self.thread_print_bot.start()

    def __call__(
        self,
        message: str,
        message_type: MessageType,
        row: int = 0,
        *args: AnyType,
        **kwargs: AnyType,
    ) -> None:
        mini_pid = self.bot.pid[:6].upper()
        tz = ZoneInfo("America/Sao_Paulo")

        if not row or row == 0:
            row = self.bot.row

        time_exec = datetime.now(tz=tz).strftime("%H:%M:%S")
        message = (
            f"[({mini_pid}, {message_type}, {row}, {time_exec})> {message}]"
        )
        msg = Message(
            pid=self.bot.pid,
            row=row,
            message=message,
            message_type=message_type,
            status="Em Execução",
            total=self.bot.total_rows,
        )
        self.queue_print_bot.put_nowait(msg)

    def print_msg(self) -> None:
        socketio_server = config.get("SOCKETIO_SERVER")
        sio = Client()

        sio.on(
            "bot_stop",
            lambda: self.bot.bot_stopped.set(),
            namespace="/bot_logs",
        )
        sio.connect(url=socketio_server, namespaces=["/bot_logs"])
        sio.emit(
            "join_room", data={"room": self.bot.pid}, namespace="/bot_logs"
        )
        while True:
            data: Message | None = None

            with suppress(Empty):
                data = self.queue_print_bot.get_nowait()

            if data:
                sio.emit("logbot", data=data, namespace="/bot_logs")
