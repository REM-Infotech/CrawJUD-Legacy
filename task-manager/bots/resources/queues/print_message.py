"""Sistema de envio de logs para o ClientUI."""

from datetime import datetime
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, TypedDict
from zoneinfo import ZoneInfo

from app.interfaces import Message
from dotenv import load_dotenv

from app.types import MessageType

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
        self.thread_print_bot = Thread()

    def __call__(self, message: str, message_type: MessageType) -> None:
        mini_pid = self.pid[:6].upper()
        tz = ZoneInfo("America/Sao_Paulo")
        time_exec = datetime.now(tz=tz).strftime("%H:%M:%S")
        message = f"[({mini_pid}, {message_type}, {self.row}, {time_exec})> {message}]"
        msg = Message(
            row=self.row,
            message=message,
            message_type=message_type,
            status=self.status,
            total=self.total_rows,
            success_count=self.success_count,
            error_count=self.error_count,
        )
        self.queue.put_nowait(msg)
