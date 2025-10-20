"""Sistema de envio de logs para o ClientUI."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from os import environ
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Lock, Thread
from typing import TYPE_CHECKING, TypedDict, cast

from __types import MessageType, StatusBot
from _interfaces import Message
from dotenv import load_dotenv
from socketio import Client

load_dotenv(Path.cwd().parent)

if TYPE_CHECKING:
    from bots.head import CrawJUD


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

    @property
    def row(self) -> int:
        return self.bot.row

    @property
    def total_rows(self) -> int:
        return self.bot.total_rows

    @property
    def pid(self) -> str:
        return self.bot.pid

    @property
    def bot_stopped(self) -> Event:
        return self.bot.bot_stopped

    @property
    def status(self) -> StatusBot:
        if self.total_rows == 0:
            return "Inicializando"

        if self.bot_stopped.is_set():
            return "Finalizado"

        return "Em Execução"

    @property
    def message_type(self) -> MessageType:
        return self._message_type

    @message_type.setter
    def message_type(self, _message_type: MessageType) -> None:
        self._message_type = _message_type

    @property
    def error_count(self) -> int:
        if self.status == "Inicializando":
            return 0

        if self.message_type == "error":
            self.remaining_count -= 1
            self.COUNTS["error_count"] += 1

        return self.COUNTS["error_count"]

    @property
    def success_count(self) -> int:
        if self.status == "Inicializando":
            return 0

        if self.message_type == "success":
            self.remaining_count -= 1
            self.COUNTS["success_count"] += 1

        return self.COUNTS["success_count"]

    @property
    def remainign_count(self) -> int:
        return self.COUNTS["remainign_count"]

    @remainign_count.setter
    def remaining_count(self, to_subtract: int) -> None:
        if self.COUNTS["remainign_count"] == 0:
            self.COUNTS["remainign_count"] = self.total_rows

        if self.status == "Em Execução":
            if self.COUNTS["remainign_count"] == 0:
                self.COUNTS["remainign_count"] = to_subtract

            self.COUNTS["remainign_count"] -= to_subtract

    @property
    def event_queue_bot(self) -> Event:
        return self.bot.event_queue_bot
