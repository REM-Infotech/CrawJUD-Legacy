"""Queues para execução dos bots."""

from threading import Event, Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from __types import MessageType, StatusBot
    from bots.head import CrawJUD


class BotQueues:
    """Queues para execução dos bots."""

    threads: list[Thread]

    def __init__(self, bot: CrawJUD) -> None:
        """Instância das queues para execução dos bots."""
        from .file_operation import SaveError, SaveSuccess
        from .print_message import PrintMessage

        self.bot = bot
        self.event_queue_bot = Event()

        self.print_message = PrintMessage(bot)
        self.save_success = SaveSuccess(bot)
        self.save_error = SaveError(bot)

        self.threads = [
            self.print_message.th,
            self.save_success.th,
            self.save_error.th,
        ]

    def stop_queues(self) -> None:
        self.event_queue_bot.set()

        for th in self.threads:
            th.join(15)

    @property
    def status(self) -> StatusBot:
        if self.total_rows == 0:
            return "Inicializando"

        if self.bot_stopped.is_set():
            return "Finalizado"

        return "Em Execução"

    @property
    def event_queue_bot(self) -> Event:
        return self.bot.event_queue_bot

    @event_queue_bot.setter
    def event_queue_bot(self, _event: Event) -> None:
        self.bot.event_queue_bot = _event

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
