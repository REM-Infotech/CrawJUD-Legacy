"""Operações de planilhas."""

from contextlib import suppress
from datetime import datetime
from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from pandas import DataFrame, ExcelWriter

from __types import Dict

from .head import BotQueues

DATASAVE = []

if TYPE_CHECKING:
    from bots.head import CrawJUD


class SaveSuccess(BotQueues):
    """Controle da Queue de salvamento de sucessos."""

    bot: CrawJUD

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de sucessos."""
        self.bot = bot
        self.queue = Queue()
        self.th = Thread(target=self.queue_save, daemon=True)
        self.th.start()

    def __call__(
        self,
        work_sheet: str = "Sucessos",
        data_save: list[Dict] = DATASAVE,
        *args,
        **kwargs,
    ) -> None:
        _kwarg = kwargs
        self.queue.put({
            "work_sheet": work_sheet,
            "data_save": data_save,
        })

    def queue_save(self) -> None:
        now = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).strftime(
            "%d.%m.%Y"
        )
        xlsx_name = f"Resultados - {now} - {self.pid}.xlsx"
        xlsx_file = self.bot.output_dir_path.joinpath(xlsx_name)
        xlsx_file.parent.mkdir(parents=True, exist_ok=True)

        with ExcelWriter(xlsx_file, "openpyxl", mode="w") as writer:
            DataFrame().to_excel(excel_writer=writer)

        with ExcelWriter(xlsx_file, "openpyxl", mode="a") as writer:
            while not self.event_queue_bot.is_set():
                data = None
                with suppress(Empty):
                    data = self.queue.get_nowait()

                if data:
                    df = DataFrame(data["data_save"])
                    df.to_excel(writer, data["work_sheet"])


class SaveError(BotQueues):
    """Controle da Queue de salvamento de erros."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot
        self.queue = Queue()
        self.th = Thread(target=self.queue_save, daemon=True)
        self.th.start()

    def __call__(
        self,
        work_sheet: str = "Erros",
        data_save: list[Dict] = DATASAVE,
        *args,
        **kwargs,
    ) -> None:
        self.queue.put({
            "work_sheet": work_sheet,
            "data_save": data_save,
        })

    def queue_save(self) -> None:
        now = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).strftime(
            "%d.%m.%Y"
        )
        xlsx_name = f"Erros - {now} - {self.pid}.xlsx"
        xlsx_file = self.bot.output_dir_path.joinpath(xlsx_name)
        xlsx_file.parent.mkdir(parents=True, exist_ok=True)

        with ExcelWriter(xlsx_file, "openpyxl", mode="w") as writer:
            DataFrame().to_excel(excel_writer=writer)

        with ExcelWriter(xlsx_file, "openpyxl", mode="a") as writer:
            while not self.event_queue_bot.is_set():
                data = None
                with suppress(Empty):
                    data = self.queue.get_nowait()

                if data:
                    df = DataFrame(data["data_save"])
                    df.to_excel(writer, data["work_sheet"])
