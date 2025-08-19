"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from threading import Semaphore
from typing import TYPE_CHECKING, ClassVar
from zoneinfo import ZoneInfo

from dotenv import dotenv_values
from selenium.webdriver.remote.webdriver import WebDriver
from socketio import Client
from termcolor import colored
from tqdm import tqdm

from crawjud.utils.models.logs import MessageLogDict
from crawjud.utils.storage import Storage

if TYPE_CHECKING:
    from typing import ClassVar

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait
    from socketio import SimpleClient

    from crawjud.custom.task import ContextTask
    from crawjud.interfaces.dict.bot import BotData, DictFiles

environ = dotenv_values()
func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}

work_dir = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


def print_in_thread(
    start_time: str,
    message: str,
    total_rows: int = 0,
    row: int = 0,
    errors: int = 0,
    type_log: str = "log",
    pid: str | None = None,
) -> None:
    """Envie mensagem de log para o sistema de tarefas assíncronas via SocketIO.

    Args:
        start_time (str): Horário de início do processamento.
        message (str): Mensagem a ser registrada.
        total_rows (int): Total de linhas a serem processadas.
        row (int): Linha atual do processamento.
        errors (int): Quantidade de erros.
        type_log (str): Tipo de log (info, error, etc).
        pid (str | None): Identificador do processo.

    """
    sio = Client(
        reconnection_attempts=15,
        reconnection_delay=5,
        reconnection_delay_max=10,
    )
    sio.connect(
        url=server,
        namespaces=[namespace],
        wait=True,
        wait_timeout=30,
        retry=True,
    )

    sio.emit(
        event="join_room",
        data={"data": {"room": pid}},
        namespace=namespace,
    )

    # Obtém o horário atual formatado
    time_exec = datetime.now(tz=ZoneInfo("America/Manaus")).strftime(
        "%H:%M:%S",
    )
    # Monta o prompt da mensagem
    prompt = (
        f"[({pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"
    )

    # Cria objeto de log da mensagem
    data = {
        "data": MessageLogDict(
            message=str(prompt),
            pid=str(pid),
            row=int(row),
            type=type_log,
            status="Em Execução",
            total=int(total_rows),
            success=0,
            errors=errors,
            remaining=int(total_rows),
            start_time=start_time,
        ),
    }
    sio.emit(event="log_execution", data=data, namespace=namespace)

    file_log = work_dir.joinpath("temp", pid, f"{pid}.log")
    file_log.parent.mkdir(parents=True, exist_ok=True)
    file_log.touch(exist_ok=True)

    with file_log.open("a") as f:
        # Cria objeto de log da mensagem
        tqdm.write(
            file=f,
            s=colored(
                prompt,
                color={
                    "info": "cyan",
                    "log": "white",
                    "error": "red",
                    "warning": "magenta",
                    "success": "green",
                }.get(type_log, "white"),
            ),
        )


class AbstractCrawJUD[T]:
    """Classe base para todos os bots."""

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

    semaforo_save = Semaphore(1)
    _storage = Storage("minio")

    _row: ClassVar[int] = 0

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, row: int) -> None:
        self._row = row

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
    def start_time(self) -> str:
        return self._start_time

    @start_time.setter
    def start_time(self, _start_time: str) -> None:
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
