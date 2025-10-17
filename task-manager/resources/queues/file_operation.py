"""Operações de planilhas."""

from contextlib import suppress
from queue import Empty, Queue
from threading import Event, Thread
from typing import cast

from _interfaces import BotData, DataSucesso
from bots.head import CrawJUD


class SaveSuccess:
    """Controle da Queue de salvamento de sucessos."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de sucessos."""
        self.bot = bot
        self.queue = Queue()
        self.th = Thread(target=self.queue_save_success, daemon=True)
        self.th.start()

    def __call__(self, *args, **kwds) -> None:
        pass

    def queue_save_success(self) -> None:
        while not self.event_queue_bot.is_set():
            data: BotData = None
            with suppress(Empty):
                data = cast("DataSucesso", self.queue.get_nowait())

            if data:
                print("ok")  # noqa: T201

    @property
    def event_queue_bot(self) -> Event:
        return self.bot.queue_control.event_queue_bot


class SaveError:
    """Controle da Queue de salvamento de erros."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot
        self.queue = Queue()
        self.th = Thread(target=self.queue_save_erro, daemon=True)
        self.th.start()

    def __call__(self, *args, **kwds) -> None:
        pass

    def queue_save_erro(self) -> None:
        while not self.event_queue_bot.is_set():
            data: BotData = None
            with suppress(Empty):
                data = cast("BotData", self.queue.get_nowait())

            if data:
                print("ok")  # noqa: T201

    @property
    def event_queue_bot(self) -> Event:
        return self.bot.queue_control.event_queue_bot
