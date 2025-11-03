"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import ClassVar
from zipfile import ZIP_DEFLATED, ZipFile

from celery import Celery, Task
from celery.worker.request import Request
from pandas import DataFrame, Timestamp, read_excel
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome as ChromeWired
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from werkzeug.utils import secure_filename

import _hook
from __types import AnyType, Dict, P, T
from _interfaces import BotData, ColorsDict
from constants import WORKDIR
from constants.webdriver import ARGUMENTS, PREFERENCES, SETTINGS
from resources import format_string
from resources._minio import Minio
from resources.queues.file_operation import SaveError, SaveSuccess
from resources.queues.head import BotQueues
from resources.queues.print_message import PrintMessage
from resources.web_element import WebElementBot

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

    _pid: str
    driver: Chrome
    _event_queue_bot: Event = None
    _task: Callable
    app: Celery
    var_store: ClassVar[Dict] = {}
    _bot_stopped: Event
    _frame: list[BotData] = None
    _xlsx: str = None
    _bot_data: BotData = None
    _total_rows: int = None
    _otherfiles: list[str] = None
    _anexos: list[str] = None
    _xlsx_data: list[Dict] = None
    _planilha_xlsx: str = None
    request: Request
    queue_control: BotQueues
    _credenciais: ClassVar[Dict] = {}

    def __init__(self) -> None:
        """Inicializa o CrawJUD."""
        self._task = self.run
        self.run = self.__call__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

        self._bot_stopped = Event()
        self.queue_control = BotQueues(self)
        self.setup()

        return self._task(*args, **kwargs)

    def setup(self) -> None:
        options = ChromeOptions()

        user_data_dir = WORKDIR.joinpath("chrome-data", self.request.id)
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_data_dir.chmod(0o775)

        options.add_argument(f"--user-data-dir={user_data_dir!s}")

        for argument in ARGUMENTS:
            options.add_argument(argument)

        if "projudi" in self.name:
            options.add_argument("--incognito")

        download_dir = str(self.output_dir_path)
        preferences = PREFERENCES
        preferences.update({
            "download.default_directory": download_dir,
            "printing.print_preview_sticky_settings.appState": SETTINGS,
        })

        options.add_experimental_option("prefs", preferences)

        for root, _, files in Path.cwd().joinpath("chrome-extensions").walk():
            for file in filter(lambda x: x.endswith(".crx"), files):
                options.add_extension(str(root.joinpath(file)))

        if "pje" not in self.name:
            cache_manager = DriverCacheManager()
            driver_manager = ChromeDriverManager(cache_manager=cache_manager)
            service = Service(executable_path=driver_manager.install())
            self.driver = Chrome(options=options, service=service)

        else:
            self.driver = ChromeWired(options=options)

        self.driver._web_element_cls = WebElementBot
        self.wait = WebDriverWait(self.driver, 30)

        self.download_files()
        if self.credenciais:
            self.load_credenciais()

        if self.planilha_xlsx:
            self.load_xlsx()

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

        if self.anexos:
            self._anexos = [
                format_string(anexo) for anexo in list(self._anexos)
            ]

    def load_credenciais(self) -> None:
        for k, v in list(self.credenciais.items()):
            setattr(self, k, v)

    def load_xlsx(self) -> None:
        path_xlsx = self.output_dir_path.joinpath(
            format_string(self.planilha_xlsx),
        )

        with path_xlsx.open("rb") as fp:
            self.xlsx_data = read_excel(fp, engine="openpyxl").to_dict(
                orient="records"
            )

    def download_files(self) -> None:
        client = Minio()

        for item in client.list_objects(
            "outputexec-bots",
            prefix=self.request.kwargs["folder_objeto_minio"],
            recursive=True,
        ):
            file_path = str(
                self.output_dir_path.joinpath(
                    format_string(Path(item.object_name).name)
                ),
            )
            _obj = client.fget_object(
                item.bucket_name, item.object_name, file_path
            )

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
        df = DataFrame(self.xlsx_data)
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

    def finalize_execution(self) -> None:
        """Finalize bot execution by closing browsers and logging total time.

        Performs cookie cleanup, quits the driver, and prints summary logs.
        """
        with suppress(Exception):
            window_handles = self.driver.window_handles
            if window_handles:
                self.driver.delete_all_cookies()
                self.driver.quit()

        message = "Fim da execução"
        self.print_message(message=message, message_type="success")

        zip_file = self.zip_result()
        link = self.upload_file(zipfile=zip_file)

        message = f"Baixe os resultados aqui: {link}"
        self.print_message(message=message, message_type="info")

        self.queue_control.stop_queues()

    def upload_file(self, zipfile: Path) -> str:
        client = Minio()

        client.fput_object("outputexec-bots", zipfile.name, str(zipfile))

        return client.get_presigned_url(
            "GET", "outputexec-bots", object_name=zipfile.name
        )

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
