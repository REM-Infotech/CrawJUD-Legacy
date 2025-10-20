"""Sistema de envio de logs para o ClientUI."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from os import environ
from pathlib import Path
from queue import Empty, Queue
from threading import Lock, Thread
from typing import TYPE_CHECKING, TypedDict, cast

from dotenv import load_dotenv
from socketio import Client

from __types import MessageType
from _interfaces import Message

from .head import BotQueues

if TYPE_CHECKING:
    from bots.head import CrawJUD

load_dotenv(Path.cwd().parent)


class Count(TypedDict):
    """Dicionario de contagem."""

    success_count: int = 0
    remainign_count: int = 0
    error_count: int = 0


class PrintMessage(BotQueues):
    """Envio de logs para o FrontEnd."""

    bot: CrawJUD
    _message_type: MessageType

    def __init__(self, bot: CrawJUD) -> None:
        """Inicializa o PrintMessage."""
        self.bot = bot
        self.COUNTS = Count(success_count=0, error_count=0, remainign_count=0)
        self.message_locker = Lock()
        self.queue = Queue()

        self.th = Thread(target=self.queue_message)
        self.th.start()

    def __call__(self, message: str, message_type: MessageType) -> None:
        self.message_type = message_type

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

    def queue_message(self) -> None:
        uri = f"http://{environ['SOCKETIO_SERVER']}"

        sio = Client()
        sio.connect(uri, namespaces=["/bot_logs"])

        self.sio = sio

        Thread(target=sio.wait).start()

        @sio.on("bot_stop", namespace="/bot_logs")
        def stop_bot() -> None:
            self.bot_stopped.set()

        with ThreadPoolExecutor(max_workers=4) as pool:
            while not self.event_queue_bot.is_set():
                data: Message = None
                with suppress(Empty):
                    data = cast("Message", self.queue.get_nowait())

                if data:
                    pool.submit(self.print_message, **data)

    def print_message(self, **kwargs) -> None:
        data: Message = kwargs
        with self.message_locker, suppress(Exception):
            self.sio.emit(
                "join_room",
                data={"room": self.pid},
                namespace="/bot_logs",
            )

            self.sio.emit("log_bot", data=data, namespace="/bot_logs")
