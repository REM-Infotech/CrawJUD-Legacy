"""Queues para execução dos bots."""

from threading import Event, Thread
from typing import TYPE_CHECKING

from .file_operation import SaveError, SaveSuccess
from .print_message import PrintMessage

if TYPE_CHECKING:
    from bots.head import CrawJUD


class BotQueues:
    """Queues para execução dos bots."""

    threads: list[Thread]

    def __init__(self, bot: CrawJUD) -> None:
        """Instância das queues para execução dos bots."""
        self.event_queue_bot = Event()

        self.print_message = PrintMessage(self)
        self.save_success = SaveSuccess(self)
        self.save_error = SaveError(self)

        self.threads = [
            self.print_message.th,
            self.save_success.th,
            self.save_error.th,
        ]

    def stop_queues(self) -> None:
        self.event_queue_bot.set()

        for th in self.threads:
            th.join(30)
