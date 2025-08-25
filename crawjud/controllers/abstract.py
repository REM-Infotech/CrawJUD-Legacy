"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from threading import Semaphore
from typing import TYPE_CHECKING, ClassVar

from tqdm import tqdm

from crawjud.utils.storage import Storage

if TYPE_CHECKING:
    from typing import ClassVar

    from selenium.webdriver.support.wait import WebDriverWait
    from socketio import SimpleClient

    from crawjud.custom.task import ContextTask
    from crawjud.interfaces.dict.bot import BotData, DictFiles
    from crawjud.utils.webdriver import DriverBot as WebDriver


func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}
work_dir = Path(__file__).cwd()


class AbstractCrawJUD[T]:
    """Classe base para todos os bots."""

    _botname: ClassVar[str] = ""
    _botsystem: ClassVar[str] = ""

    _driver: WebDriver = None
    _wait: WebDriverWait = None
    current_task: ContextTask
    sio: SimpleClient
    _stop_bot: bool = False
    _folder_storage: ClassVar[str] = ""
    _xlsx_data: ClassVar[DictFiles] = {}
    _downloaded_files: ClassVar[list[DictFiles]] = []
    _bot_data: ClassVar[list[BotData]] = {}
    posicoes_processos: ClassVar[dict[str, int]] = {}

    tasks_cls: ClassVar[dict] = {}
    # Atributos Globais
    _pid: str | None = None
    _total_rows: int = 0
    _start_time: str | None = None
    _regiao: str | None = None
    _data_regiao: list[BotData] | None = None
    _cookies: dict[str, str] | None = None
    _headers: dict[str, str] | None = None
    _base_url: str | None = None
    _frame: ClassVar[list[BotData]] = []
    _success: ClassVar[int] = 0
    _error: ClassVar[int] = 0
    _remaining: ClassVar[int] = 0
    semaforo_save = Semaphore(1)
    _storage = Storage("minio")

    _row: ClassVar[int] = 0

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, row: int) -> None:
        self._row = row

    @property
    def botname(self) -> str:
        return self._botname

    @botname.setter
    def botname(self, botname: str) -> None:
        self._botname = botname

    @property
    def botsystem(self) -> str:
        return self._botsystem

    @botsystem.setter
    def botsystem(self, botsystem: str) -> None:
        self._botsystem = botsystem

    @abstractmethod
    def execution(self) -> None:
        """Função de execução do bot."""

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """Verifica se a subclasse implementa todos os métodos obrigatórios."""
        tqdm.write("ok")

    @property
    def bot_data(self) -> BotData:
        return self._bot_data

    @bot_data.setter
    def bot_data(self, bot_data: BotData) -> None:
        self._bot_data = bot_data

    @property
    def frame(self) -> list[BotData]:
        return self._frame

    @property
    def storage(self) -> Storage:
        """Storage do CrawJUD."""
        return self._storage

    @property
    def pid(self) -> str:
        return self._pid

    @pid.setter
    def pid(self, new_pid: str) -> None:
        self._pid = new_pid

    @property
    def start_time(self) -> float:
        return self._start_time

    @start_time.setter
    def start_time(self, _start_time: float) -> None:
        self._start_time = _start_time

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @total_rows.setter
    def total_rows(self, _total_rows: int) -> None:
        self._total_rows = _total_rows

    @property
    def downloaded_files(self) -> list[DictFiles]:
        return self._downloaded_files

    @property
    def xlsx_data(self) -> DictFiles:
        return self._xlsx_data

    @property
    def folder_storage(self) -> str:
        return self._folder_storage

    @folder_storage.setter
    def folder_storage(self, _folder_storage: str) -> None:
        self._folder_storage = _folder_storage

    @property
    def output_dir_path(self) -> Path:
        out_dir = work_dir.joinpath("temp", self.pid)

        out_dir.mkdir(parents=True, exist_ok=True)

        return out_dir

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def wait(self) -> WebDriverWait:
        return self._wait

    def search(self, *args: T, **kwargs: T) -> T:
        return NotImplementedError("Necessário implementar função!")

    def auth(self, *args: T, **kwargs: T) -> T:
        return NotImplementedError("Necessário implementar função!")

    @property
    def success(self) -> int:
        return self._success

    @success.setter
    def success(self, success: int) -> int:
        self._success = success

    @property
    def error(self) -> int:
        return self._error

    @error.setter
    def error(self, error: int) -> int:
        self._error = error

    @property
    def remaining(self) -> int:
        return self._remaining

    @remaining.setter
    def remaining(self, remaining: int) -> None:
        self._remaining = remaining
