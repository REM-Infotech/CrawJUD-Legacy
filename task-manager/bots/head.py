"""Abstração CrawJUD."""

from __future__ import annotations

import json
from abc import abstractmethod
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import ClassVar
from zipfile import ZIP_DEFLATED, ZipFile

import _hook
from __types import AnyType, Dict, P, T
from _interfaces import BotData, ColorsDict
from celery import Celery, Task
from constants import WORKDIR
from minio import Minio
from minio.credentials.providers import EnvMinioProvider
from pandas import Timestamp, read_excel
from resources.queues import BotQueues, SaveError, SaveSuccess
from resources.queues.print_message import PrintMessage
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome
from werkzeug.utils import secure_filename

__all__ = ["_hook"]
func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}


COLORS_DICT: ColorsDict = {
    "info": "cyan",
    "log": "yellow",
    "error": "red",
    "warning": "magenta",
    "success": "green",
}


class CrawJUD(Task):
    """Classe CrawJUD."""

    _task: Callable
    app: Celery
    var_store: ClassVar[Dict] = {}
    _bot_stopped: Event
    _frame: list[BotData] = None
    _xlsx: str = None
    _bot_data: BotData = None
    _total_rows: int = None

    def __init__(self) -> None:
        """Inicializa o CrawJUD."""
        self._task = self.run
        self.run = self.__call__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        self._bot_stopped = Event()
        self.queue_control = BotQueues(self)
        self.setup()

        return self._task(*args, **kwargs)

    def setup(self) -> None:
        options = ChromeOptions()

        user_data_dir = WORKDIR.joinpath("chrome-data", self.request.id)
        user_data_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir!s}")

        user_data_dir.chmod(0o775)

        self.driver = Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)

        self.download_files()
        self.load_config()

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

    def load_config(self) -> None:
        json_config = self.output_dir_path.joinpath("configuration.json")

        with json_config.open("rb") as fp:
            data = json.load(fp)

            for k, v in list(data.items()):
                setattr(self, k, v)

    def download_files(self) -> None:
        uri = self.app.conf["app_domain"]
        client = Minio(
            endpoint=f"{uri}:19000",
            credentials=EnvMinioProvider(),
            secure=False,
        )

        for item in client.list_objects(
            "outputexec-bots",
            prefix=self.request.kwargs["cod_rastreio"],
            recursive=True,
        ):
            file_path = str(
                self.output_dir_path.joinpath(
                    secure_filename(Path(item.object_name).name)
                ),
            )
            client.fget_object(item.bucket_name, item.object_name, file_path)

    def zip_result(self) -> Path:
        zip_filename = f"{self.pid[:6].upper()}.zip"
        source_dir = self.output_dir_path
        output_dir = WORKDIR.joinpath("archives", zip_filename)

        output_dir.parent.mkdir(exist_ok=True, parents=True)

        with ZipFile(output_dir, "w", ZIP_DEFLATED) as zipfile:
            for root, _, files in source_dir.walk():
                for file in files:
                    if self.pid in file and ".log" not in file:
                        file_path = root.joinpath(file)
                        arcname = file_path.relative_to(source_dir)
                        zipfile.write(file_path, arcname)

        return output_dir

    def load_data(self) -> list[BotData]:
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.


        Returns:
            list[BotData]: A record list from the processed Excel file.

        """
        self.path_planilha = self.output_dir_path.joinpath(self.xlsx)

        df = read_excel(self.path_planilha, engine="openpyxl")
        df.columns = df.columns.str.upper()

        def format_data(x: AnyType) -> str:
            if str(x) == "NaT" or str(x) == "nan":
                return ""

            if isinstance(x, (datetime, Timestamp)):
                return x.strftime("%d/%m/%Y")

            return x

        def format_float(x: AnyType) -> str:
            return f"{x:.2f}".replace(".", ",")

        for col in df.columns:
            df[col] = df[col].apply(format_data)

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(format_float)

        data_bot = []

        for item in [
            BotData(list(item.items())) for item in df.to_dict(orient="records")
        ]:
            dt = {}

            for k, v in list(item.items()):
                dt[k.upper()] = v

            if dt:
                data_bot.append(dt)

        return data_bot

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
        return self.request.id or "unknown"

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

    @abstractmethod
    def auth(self) -> bool:
        """Autenticação no sistema."""
        ...

    @property
    def botname(self) -> str:
        return str(self.name.split(".")[-1])

    @property
    def append_success(self) -> SaveSuccess:
        return self.queue_control.save_success

    @property
    def append_error(self) -> SaveError:
        return self.queue_control.save_error
