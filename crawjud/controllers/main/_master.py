"""Abstração CrawJUD."""

from __future__ import annotations

import traceback
from abc import abstractmethod
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Event, Semaphore, Thread
from typing import TYPE_CHECKING, ClassVar
from uuid import uuid4
from zoneinfo import ZoneInfo

from pandas import DataFrame, ExcelWriter
from socketio import Client
from termcolor import colored
from tqdm import tqdm

from crawjud.utils.models.logs import MessageLogDict
from crawjud.utils.storage import Storage

COLORS_DICT = {
    "info": "cyan",
    "log": "yellow",
    "error": "red",
    "warning": "magenta",
    "success": "green",
}
if TYPE_CHECKING:
    from queue import Queue
    from typing import ClassVar

    from selenium.webdriver.support.wait import WebDriverWait
    from socketio import SimpleClient

    from crawjud.custom.task import ContextTask
    from crawjud.interfaces.dict.bot import BotData, DictFiles
    from crawjud.interfaces.types import ProcessInfo
    from crawjud.utils.webdriver import DriverBot as WebDriver


func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}
work_dir = Path(__file__).cwd()


class AbstractCrawJUD[T]:
    """Classe base para todos os bots."""

    thread_copia_integral: Thread = None
    _botname: ClassVar[str] = ""
    _botsystem: ClassVar[str] = ""
    _token: ClassVar[str] = ""
    _driver: WebDriver = None
    _wait: WebDriverWait = None
    current_task: ContextTask
    sio: SimpleClient
    _stop_bot: bool = False
    url_segunda_instancia: ClassVar[str] = ""
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

    event_stop_bot: Event
    queue_msg: Queue
    queue_files: Queue
    queue_save_xlsx: Queue

    event_queue_message: Event
    event_queue_files: Event
    event_queue_save_xlsx: Event

    to_add_partes: ClassVar[list[ProcessInfo]] = []

    to_add_processos: ClassVar[list[ProcessInfo]] = []
    to_add_assuntos: ClassVar[list[ProcessInfo]] = []
    to_add_audiencias: ClassVar[list[ProcessInfo]] = []
    to_add_representantes: ClassVar[list[ProcessInfo]] = []
    to_add_processos_primeiro_grau: ClassVar[list[ProcessInfo]] = []
    to_add_processos_segundo_grau: ClassVar[list[ProcessInfo]] = []
    _pbar: ClassVar[tqdm] = None

    _window_busca_processo: ClassVar[str] = ""
    _main_window: ClassVar[str] = ""

    @property
    def main_window(self) -> str:
        return self._main_window

    @main_window.setter
    def main_window(self, main_window: str) -> None:
        self._main_window = main_window

    @property
    def window_busca_processo(self) -> str:
        return self._window_busca_processo

    @window_busca_processo.setter
    def window_busca_processo(self, window_busca_processo: str) -> None:
        self._window_busca_processo = window_busca_processo

    @property
    def current_time(self) -> str:
        return datetime.now(ZoneInfo("America/Manaus")).strftime(
            "%d-%m-%Y %H.%M.%S",
        )

    @property
    def pbar(self) -> tqdm:
        return self._pbar

    @pbar.setter
    def pbar(self, pbar: tqdm) -> None:
        self._pbar = pbar

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, token: str) -> None:
        self._token = token

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
        bot_data_ = bot_data
        for k, v in list(bot_data.items()):
            bot_data_[k.upper()] = v

        self._bot_data = bot_data_

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

    def print_in_thread(self) -> None:
        """Envie mensagem de log para o sistema de tarefas assíncronas via SocketIO.

        Args:
            locker (Lock): locker
            start_time (str): Horário de início do processamento.
            message (str): Mensagem a ser registrada.
            total_rows (int): Total de linhas a serem processadas.
            row (int): Linha atual do processamento.
            errors (int): Quantidade de erros.
            type_log (str): Tipo de log (info, error, etc).
            pid (str | None): Identificador do processo.

        """
        from dotenv import dotenv_values

        environ = dotenv_values()
        transports = ["websocket"]
        headers = {"Content-Type": "application/json"}

        server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
        namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")
        sio = Client()

        @sio.on(event="stop_bot", namespace="/logsbot")
        def stop_bot[T](*args: T, **kwargs: T) -> None:
            """Receba evento para parar o bot via SocketIO.

            Args:
                *args (T): Argumentos posicionais recebidos do evento.
                **kwargs (T): Argumentos nomeados recebidos do evento.

            """
            self.print_msg(
                message="Encerrando execução do bot...",
                type_log="info",
            )
            self.event_stop_bot.set()

        try:
            sio.connect(
                url=server,
                namespaces=[namespace],
                transports=transports,
                headers=headers,
            )

        except Exception as e:
            tqdm.write("\n".join(traceback.format_exception(e)))
            return

        while True:
            current_time = datetime.now(tz=ZoneInfo("America/Manaus"))

            setted_event = self.event_queue_message.is_set()
            empty_queue = self.queue_msg.unfinished_tasks == 0
            if setted_event and empty_queue:
                break

            data = self.queue_msg.get()
            if data:
                with suppress(Exception):
                    # Argumentos Necessários
                    start_time: str = data.get("start_time")
                    message: str = data.get("message")
                    total_rows: int = data.get("total_rows")
                    row: int = data.get("row")
                    error: int = data.get("error")
                    success: int = data.get("success")
                    type_log: str = data.get("type_log")
                    pid: str = str(data.get("pid", uuid4().hex))

                    # Formata o horário atual
                    time_exec = current_time.strftime("%H:%M:%S")

                    # Obtém o PID reduzido
                    mini_pid = pid[:6].upper()

                    # Monta o prompt da mensagem
                    message = f"[({mini_pid}, {type_log}, {row}, {time_exec})> {message}]"

                    # Cria objeto de log da mensagem

                    # Envia o log da execução
                    with suppress(Exception):
                        Thread(
                            target=sio.emit,
                            kwargs={
                                "event": "join_room",
                                "data": {"data": {"room": self.pid}},
                                "namespace": namespace,
                            },
                            daemon=True,
                        ).start()

                    with suppress(Exception):
                        Thread(
                            target=sio.emit,
                            kwargs={
                                "event": "log_execution",
                                "data": {
                                    "data": MessageLogDict(
                                        message=str(message),
                                        pid=str(pid),
                                        row=int(row),
                                        type=type_log,
                                        status="Em Execução",
                                        total=int(total_rows),
                                        success=success,
                                        error=error,
                                        remaining=int(total_rows),
                                        start_time=datetime.fromtimestamp(
                                            start_time,
                                            tz=ZoneInfo("America/Manaus"),
                                        ).strftime("%d/%m/%Y %H:%M:%S"),
                                    ),
                                },
                                "namespace": namespace,
                            },
                            daemon=True,
                        ).start()

                    # Cria o caminho do arquivo de log

                    file_log = work_dir.joinpath(
                        "temp",
                        pid,
                        f"{mini_pid}.log",
                    )

                    # Cria o diretório pai, se não existir
                    file_log.parent.mkdir(parents=True, exist_ok=True)

                    # Cria o arquivo de log, se não existir
                    file_log.touch(exist_ok=True)

                    # Define a cor da mensagem
                    colour = COLORS_DICT.get(type_log, "white")
                    colored_msg = colored(message, color=colour)

                    # Adiciona a mensagem ao arquivo de log
                    with file_log.open("a") as f:
                        # Adiciona a mensagem ao arquivo de log
                        tqdm.write(file=f, s=colored_msg)

                    # Adiciona a mensagem ao console
                    tqdm.write(colored_msg)

                    if type_log == "success" or type_log == "error":
                        with suppress(Exception):
                            if self.pbar:
                                self.pbar.update()

                # Finaliza a tarefa da fila
                self.queue_msg.task_done()

    def save_file(self) -> None:
        """Consome itens da fila `queue_save_xlsx` e adiciona na planilha.

        Encerra quando receber o sentinela (None).

        """
        nome_planilha = f"Planilha Resultados - {self.pid}.xlsx"
        path_planilha = self.output_dir_path.joinpath(nome_planilha)

        # cria/abre arquivo para APPEND
        # pandas >= 2.0: if_sheet_exists=('replace'|'overlay'|'new'), funciona só em mode='a'
        while True:
            setted_event = self.event_stop_bot.is_set()
            empty_queue = self.queue_save_xlsx.unfinished_tasks == 0

            if setted_event and empty_queue:
                break

            data = self.queue_save_xlsx.get()

            if data:
                try:
                    rows = data["to_save"]
                    sheet_name = data["sheet_name"]

                    if not isinstance(rows, list):
                        rows = [rows]

                    df = DataFrame(rows)

                    # Remove timezone de todas as colunas possíveis para evitar erro no Excel
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
                    if path_planilha.exists():
                        with ExcelWriter(
                            path=path_planilha,
                            mode="a",
                            engine="openpyxl",
                            if_sheet_exists="overlay",
                        ) as writer:
                            # pega a aba (se existir) e calcula a próxima linha
                            wb = writer.book
                            ws = (
                                wb[sheet_name]
                                if sheet_name in wb.sheetnames
                                else wb.create_sheet(sheet_name)
                            )
                            startrow = (
                                ws.max_row if ws.max_row > 1 else 0
                            )  # 0 => escreve com header
                            write_header = startrow == 0
                            df.to_excel(
                                excel_writer=writer,
                                sheet_name=sheet_name,
                                index=False,
                                header=write_header,
                                startrow=startrow,
                            )
                    else:
                        # primeira escrita cria arquivo e cabeçalho
                        with ExcelWriter(
                            path=path_planilha,
                            mode="w",
                            engine="openpyxl",
                        ) as writer:
                            df.to_excel(
                                excel_writer=writer,
                                sheet_name=sheet_name,
                                index=False,
                            )

                except Exception as e:
                    # logue o stack completo (não interrompe o consumidor)
                    tqdm.write("\n".join(traceback.format_exception(e)))

                finally:
                    self.queue_save_xlsx.task_done()
