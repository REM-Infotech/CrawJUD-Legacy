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
        self.queue.put_nowait({
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

        while not self.event_queue_bot.is_set():
            data = None
            with suppress(Empty):
                data = self.queue.get_nowait()

            if data:
                list_data = data["data_save"]
                sheet = data["work_sheet"]
                df = DataFrame(list_data)
                for col in df.columns:
                    with suppress(Exception):
                        df[col] = df[col].apply(
                            lambda x: x.tz_localize(None)
                            if hasattr(x, "tz_localize")
                            else x,
                        )
                        continue

                    with suppress(Exception):
                        df[col] = df[col].apply(
                            lambda x: x.tz_convert(None)
                            if hasattr(x, "tz_convert")
                            else x,
                        )
                # --- APPEND na mesma aba, calculando a próxima linha ---
                if not xlsx_file.exists():
                    # primeira escrita cria arquivo e cabeçalho
                    with ExcelWriter(
                        path=xlsx_file,
                        mode="w",
                        engine="openpyxl",
                    ) as writer:
                        df.to_excel(
                            excel_writer=writer,
                            sheet_name=sheet,
                            index=False,
                        )

                    continue

                with ExcelWriter(
                    path=xlsx_file,
                    mode="a",
                    engine="openpyxl",
                    if_sheet_exists="overlay",
                ) as writer:
                    # pega a aba (se existir) e calcula a próxima linha
                    wb = writer.book
                    ws = (
                        wb[sheet]
                        if sheet in wb.sheetnames
                        else wb.create_sheet(sheet)
                    )
                    startrow = (
                        int(ws.max_row) if int(ws.max_row) > 1 else 0
                    )  # 0 => escreve com header
                    write_header = int(startrow) == 0
                    df.to_excel(
                        excel_writer=writer,
                        sheet_name=sheet,
                        index=False,
                        header=write_header,
                        startrow=startrow,
                    )


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
    ) -> None:
        self.queue.put_nowait({
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

        while not self.event_queue_bot.is_set():
            data = None
            with suppress(Empty):
                data = self.queue.get_nowait()

            if data:
                list_data = data["data_save"]
                sheet = data["work_sheet"]
                df = DataFrame(list_data)
                for col in df.columns:
                    with suppress(Exception):
                        df[col] = df[col].apply(
                            lambda x: x.tz_localize(None)
                            if hasattr(x, "tz_localize")
                            else x,
                        )
                        continue

                    with suppress(Exception):
                        df[col] = df[col].apply(
                            lambda x: x.tz_convert(None)
                            if hasattr(x, "tz_convert")
                            else x,
                        )
                # --- APPEND na mesma aba, calculando a próxima linha ---
                if not xlsx_file.exists():
                    # primeira escrita cria arquivo e cabeçalho
                    with ExcelWriter(
                        path=xlsx_file,
                        mode="w",
                        engine="openpyxl",
                    ) as writer:
                        df.to_excel(
                            excel_writer=writer,
                            sheet_name=sheet,
                            index=False,
                        )

                    continue

                with ExcelWriter(
                    path=xlsx_file,
                    mode="a",
                    engine="openpyxl",
                    if_sheet_exists="overlay",
                ) as writer:
                    # pega a aba (se existir) e calcula a próxima linha
                    wb = writer.book
                    ws = (
                        wb[sheet]
                        if sheet in wb.sheetnames
                        else wb.create_sheet(sheet)
                    )
                    startrow = (
                        int(ws.max_row) if int(ws.max_row) > 1 else 0
                    )  # 0 => escreve com header
                    write_header = int(startrow) == 0
                    df.to_excel(
                        excel_writer=writer,
                        sheet_name=sheet,
                        index=False,
                        header=write_header,
                        startrow=startrow,
                    )
