"""Operações de planilhas."""

from contextlib import suppress
from datetime import datetime
from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING, NoReturn
from zoneinfo import ZoneInfo

from pandas import DataFrame, ExcelWriter, concat, read_excel

from app.types import Dict

DATASAVE = []

if TYPE_CHECKING:
    from bots.head import CrawJUD


class SaveSuccess:
    """Controle da Queue de salvamento de sucessos."""

    bot: CrawJUD

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot

        self.queue_save = Queue()
        self.thead_save = Thread(target=self.save_success, daemon=True)
        self.thead_save.start()

    def __call__(self, work_sheet: str, data_save: str) -> None:
        self.queue_save.put_nowait({
            "work_sheet": work_sheet,
            "data_save": data_save,
        })

    def save_success(self) -> NoReturn:
        tz = ZoneInfo("America/Sao_Paulo")
        now = datetime.now(tz=tz).strftime("%d-%m-%Y %H-%M-%S")
        nome_arquivo = f"Sucessos - PID {self.bot.pid} - {now}.xlsx"
        arquivo_sucesso = self.bot.output_dir_path.joinpath(nome_arquivo)
        while True:
            data: Dict | None = None

            with suppress(Empty):
                data = self.queue_save.get_nowait()

            if data:
                with suppress(Exception):
                    df = DataFrame(data["data_save"])
                    if arquivo_sucesso.exists():
                        df = concat([
                            read_excel(
                                arquivo_sucesso,
                                engine="openpyxl",
                                sheet_name=data["work_sheet"],
                            ),
                            DataFrame(data["data_save"]),
                        ])

                    with ExcelWriter(
                        arquivo_sucesso, engine="openpyxl"
                    ) as writer:
                        df.to_excel(
                            excel_writer=writer, sheet_name=data["work_sheet"]
                        )


class SaveError:
    """Controle da Queue de salvamento de erros."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot
        self.queue_save = Queue()
        self.thead_save = Thread(target=self.save_error, daemon=True)
        self.thead_save.start()

    def __call__(self, work_sheet: str, data_save: list[Dict]) -> None:
        self.queue_save.put_nowait({
            "work_sheet": work_sheet,
            "data_save": data_save,
        })

    def save_error(self) -> NoReturn:
        tz = ZoneInfo("America/Sao_Paulo")
        now = datetime.now(tz=tz).strftime("%d-%m-%Y %H-%M-%S")
        nome_arquivo = f"Erros - PID {self.bot.pid} - {now}.xlsx"
        arquivo_sucesso = self.bot.output_dir_path.joinpath(nome_arquivo)
        while True:
            data: Dict | None = None

            with suppress(Empty):
                data = self.queue_save.get_nowait()

            if data:
                with suppress(Exception):
                    df = DataFrame(data["data_save"])
                    if arquivo_sucesso.exists():
                        df = concat([
                            read_excel(
                                arquivo_sucesso,
                                engine="openpyxl",
                                sheet_name=data["work_sheet"],
                            ),
                            DataFrame(data["data_save"]),
                        ])

                    with ExcelWriter(
                        arquivo_sucesso, engine="openpyxl"
                    ) as writer:
                        df.to_excel(
                            excel_writer=writer, sheet_name=data["work_sheet"]
                        )
