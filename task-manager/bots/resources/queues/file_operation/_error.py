from datetime import datetime
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, NoReturn
from zoneinfo import ZoneInfo

from pandas import DataFrame

from app.interfaces import DataSave
from bots.resources.iterators.queue import QueueIterator
from bots.resources.queues.file_operation._main import FileOperator

DATASAVE = []

if TYPE_CHECKING:
    from app.types import Dict
    from bots.head import CrawJUD


class SaveError(FileOperator):
    """Controle da Queue de salvamento de erros."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot
        self.queue_save = Queue()
        self.thead_save = Thread(target=self.save_error, daemon=True)
        self.thead_save.start()

    def __call__(self, worksheet: str, data_save: list[Dict]) -> None:
        self.queue_save.put_nowait({
            "worksheet": worksheet,
            "data_save": DataFrame(data_save).to_dict(orient="records"),
        })

    def save_error(self) -> NoReturn:
        tz = ZoneInfo("America/Sao_Paulo")
        now = datetime.now(tz=tz).strftime("%d-%m-%Y %H-%M-%S")
        nome_arquivo = f"Erros - PID {self.bot.pid} - {now}.xlsx"
        arquivo_erro = self.bot.output_dir_path.joinpath(nome_arquivo)

        for data in QueueIterator[DataSave](self.queue_save):
            if data and len(data["data_save"] > 0):
                self.save_file(data=data, arquivo_xlsx=arquivo_erro)
