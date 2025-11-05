from __future__ import annotations

from pathlib import Path
from threading import Event

from celery import Task
from werkzeug.utils import secure_filename

from __types import Dict
from _interfaces import BotData
from constants import WORKDIR
from resources.queues.file_operation import SaveError, SaveSuccess
from resources.queues.print_message import PrintMessage


class HeadCrawJUD(Task):
    @property
    def print_message(self) -> PrintMessage:
        return self.queue_control.print_message

    @property
    def bot_stopped(self) -> Event:
        return self._bot_stopped

    @property
    def row(self) -> int:
        return self.var_store.get("row", 0)

    @row.setter
    def row(self, _new_row: int) -> None:
        self.var_store["row"] = _new_row

    @property
    def pid(self) -> str:
        return self._pid

    @pid.setter
    def pid(self, _pid: str) -> None:
        self._pid = _pid

    @property
    def output_dir_path(self) -> Path:
        return WORKDIR.joinpath("output", self.pid)

    @property
    def total_rows(self) -> int:
        return self.var_store.get("total_rows", 0)

    @total_rows.setter
    def total_rows(self, _total_rows: int) -> None:
        self.var_store["total_rows"] = _total_rows

    @property
    def xlsx(self) -> str:
        return self._xlsx

    @xlsx.setter
    def xlsx(self, _xlsx: str) -> None:
        self._xlsx = secure_filename(_xlsx)

    @property
    def bot_data(self) -> BotData:
        return self._bot_data

    @bot_data.setter
    def bot_data(self, new_data: BotData) -> None:
        self._bot_data = new_data

    @property
    def frame(self) -> list[BotData]:
        if not self._frame:
            self._frame = self.load_data()

        return self._frame

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @total_rows.setter
    def total_rows(self, _total_rows: int) -> None:
        self._total_rows = _total_rows

    @property
    def botname(self) -> str:
        return str(self.name.split(".")[-1])

    @property
    def append_success(self) -> SaveSuccess:
        return self.save_success

    @property
    def append_error(self) -> SaveError:
        return self.save_error

    @property
    def event_queue_bot(self) -> Event:
        return self._event_queue_bot

    @event_queue_bot.setter
    def event_queue_bot(self, event: Event) -> None:
        self._event_queue_bot = event

    @property
    def otherfiles(self) -> list[str]:
        return self._otherfiles

    @otherfiles.setter
    def otherfiles(self, _other_files: list[str]) -> None:
        self._otherfiles = _other_files

    @property
    def credenciais(self) -> Dict:
        return self._credenciais

    @credenciais.setter
    def credenciais(self, _credenciais: Dict) -> None:
        self._credenciais = _credenciais

    @property
    def xlsx_data(self) -> list[Dict]:
        return self._xlsx_data

    @xlsx_data.setter
    def xlsx_data(self, _xlsx_data: list[Dict]) -> None:
        self._xlsx_data = _xlsx_data

    @property
    def planilha_xlsx(self) -> str:
        return self._planilha_xlsx

    @planilha_xlsx.setter
    def planilha_xlsx(self, new_val: str) -> None:
        self._planilha_xlsx = new_val

    @property
    def anexos(self) -> list[str]:
        return self._anexos

    @anexos.setter
    def anexos(self, anexos: str) -> None:
        self._anexos = anexos
