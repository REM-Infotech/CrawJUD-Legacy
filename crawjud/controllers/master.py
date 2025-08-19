"""Modulo de controle da classe Base para todos os bots."""

from __future__ import annotations

import json
import shutil
from abc import abstractmethod
from contextlib import suppress
from datetime import datetime
from io import BytesIO
from pathlib import Path
from threading import Semaphore, Thread
from time import sleep
from typing import TYPE_CHECKING, ClassVar, Literal
from zoneinfo import ZoneInfo

import base91
import pandas as pd
from pandas import Timestamp, read_excel
from selenium.webdriver.remote.webdriver import WebDriver
from termcolor import colored
from tqdm import tqdm
from werkzeug.utils import secure_filename

from crawjud.common import name_colunas
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.custom.task import ContextTask
from crawjud.interfaces.dict.bot import BotData, DictFiles
from crawjud.utils.models.logs import MessageLogDict
from crawjud.utils.storage import Storage
from crawjud.utils.webdriver import DriverBot

if TYPE_CHECKING:
    from typing import ClassVar

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait
    from socketio import SimpleClient


func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}

work_dir = Path(__file__).cwd()


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


class CrawJUD[T](AbstractCrawJUD, ContextTask):
    """Classe CrawJUD."""

    def __init__(self) -> None:
        """Inicialize a instância principal do controller CrawJUD.

        Args:
            self: Instância do objeto.

        """
        self._driver = DriverBot(
            selected_browser="chrome",
            with_proxy=False,
        )

        self._wait = self._driver.wait

    def load_data(self) -> list[BotData]:
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.

        Arguments:
            base91_planilha (str):
                base91 da planilha

        Returns:
            list[BotData]: A record list from the processed Excel file.

        """
        xlsx_b91 = self._xlsx_data["file_base91str"]
        decoded_b91 = base91.decode(xlsx_b91)
        buffer_planilha = BytesIO(decoded_b91)

        df = read_excel(buffer_planilha)
        df.columns = df.columns.str.upper()

        def format_data(x: T) -> str:
            if str(x) == "NaT" or str(x) == "nan":
                return ""

            if isinstance(x, (datetime, Timestamp)):
                return x.strftime("%d/%m/%Y")

            return x

        def format_float(x: T) -> str:
            return f"{x:.2f}".replace(".", ",")

        for col in df.columns:
            df[col] = df[col].apply(format_data)

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(format_float)

        return [
            BotData(list(item.items()))
            for item in df.to_dict(orient="records")
        ]

    def download_files(
        self,
    ) -> None:
        # TODO(Nicholas Silva): Criar Exception para erros de download de arquivos
        # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
        """Baixa os arquivos necessários para a execução do robô.

        Raises:
            ExecutionError:
                Exception genérico de execução

        """
        storage = Storage("minio")
        path_files = work_dir.joinpath("temp")
        list_files: list[DictFiles] = []

        folder_temp_ = self.folder_storage.upper()
        json_name_ = f"{self.folder_storage}.json"

        object_name_ = Path(folder_temp_).joinpath(json_name_).as_posix()
        config_file = storage.bucket.get_object(object_name_)

        path_files.joinpath(object_name_).parent.mkdir(
            exist_ok=True,
            parents=True,
        )

        data_json_: dict[str, str] = json.loads(config_file.data)

        for k, v in data_json_.items():
            setattr(self, k, v)

        if data_json_.get("xlsx"):
            xlsx_name_ = secure_filename(data_json_.get("xlsx"))

            path_minio_ = Path(folder_temp_).joinpath(xlsx_name_).as_posix()
            file_xlsx = storage.bucket.get_object(path_minio_)
            file_base91str = base91.encode(file_xlsx.data)

            suffix_ = Path(xlsx_name_).suffix

            list_files.append(
                DictFiles(
                    file_name=xlsx_name_,
                    file_base91str=file_base91str,
                    file_suffix=suffix_,
                ),
            )

        if data_json_.get("otherfiles"):
            files_list: list[str] = data_json_.get("otherfiles")
            for file in files_list:
                file = secure_filename(file)
                path_minio_ = Path(folder_temp_).joinpath(file).as_posix()
                file_ = storage.bucket.get_object(path_minio_)
                suffix_ = Path(file).suffix

                file_base91str = base91.encode(file_.data)
                list_files.append(
                    DictFiles(
                        file_name=file,
                        file_base91str=file_base91str,
                        file_suffix=suffix_,
                    ),
                )

        shutil.rmtree(path_files.joinpath(self.folder_storage))

        xlsx_key = list(
            filter(lambda x: x["file_suffix"] == ".xlsx", list_files),
        )
        if not xlsx_key:
            raise ExecutionError(message="Nenhum arquivo Excel encontrado.")

        _json_key = list(
            filter(lambda x: x["file_suffix"] == ".json", list_files),
        )

        self._xlsx_data = xlsx_key[-1]
        self._downloaded_files = list_files

    def data_frame(self) -> None:
        bot_data: list[BotData] = self.load_data()
        self._frame = bot_data
        self._bot_data = bot_data

    def carregar_arquivos(self) -> None:
        self.download_files()
        self.data_frame()

        self.print_msg(
            message="Planilha carregada!",
            type_log="info",
        )

    def print_msg(
        self,
        message: str,
        row: int = 0,
        errors: int = 0,
        type_log: str = "log",
    ) -> None:
        """Imprime mensagem de log do processo.

        Args:
            self: Instância do objeto.
            message (str): Mensagem a ser exibida.
            row (int): Linha do processo.
            errors (int): Quantidade de erros.
            type_log (str): Tipo de log.

        """
        """Envia mensagem de log para o sistema de tarefas assíncronas.

        Args:
            pid (str): Identificador do processo.
            message (str): Mensagem a ser registrada.
            row (int): Linha atual do processamento.
            type_log (str): Tipo de log (info, error, etc).
            total_rows (int): Total de linhas a serem processadas.
            start_time (str): Horário de início do processamento.
            status (str): Status atual do processamento (default: "Em Execução").



        """
        # Obtém o horário atual formatado
        time_exec = datetime.now(tz=ZoneInfo("America/Manaus")).strftime(
            "%H:%M:%S",
        )
        # Monta o prompt da mensagem
        prompt = f"[({self._pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"

        # Cria objeto de log da mensagem
        data = {
            "data": MessageLogDict(
                message=str(prompt),
                pid=str(self._pid),
                row=int(row),
                type=type_log,
                status="Em Execução",
                total=int(self._total_rows),
                success=0,
                errors=errors,
                remaining=int(self._total_rows),
                start_time=self._start_time,
            ),
        }

        sleep(2)

        Thread(
            target=self.sio.emit,
            kwargs={
                "event": "log_execution",
                "data": data,
            },
        ).start()

        file_log = work_dir.joinpath("temp", self.pid, f"{self.pid}.log")
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

    def append_success(
        self,
        data: BotData,
        message: str | None = None,
        file_name_success: str | None = None,
        type_log: str = "success",
    ) -> None:
        """Registre dados de sucesso em planilha de execuções bem-sucedidas.

        Args:
            data (BotData): Dados a serem registrados.
            message (str, opcional): Mensagem de sucesso para log.
            file_name_success (str, opcional): Nome do arquivo para salvar os dados.
            type_log (str): Tipo de log (default: "success").

        """
        # Define mensagem padrão caso não seja fornecida
        if not message:
            message = "Execução do processo efetuada com sucesso!"

        # Função auxiliar para salvar informações em Excel
        def save_info(
            data: list[dict[str, str]],
            file_name_success: str | None,
        ) -> None:
            output_success = self.output_dir_path.joinpath(file_name_success)
            excel_writer = pd.ExcelWriter(
                path=str(output_success),
                engine="openpyxl",
                mode="w",
            )
            with excel_writer as writer:
                df = pd.DataFrame(data)
                # Caso a planilha já exista, calcula a próxima linha
                row_start = 0

                with suppress(Exception):
                    row_start = int(writer.book["Sucessos"].max_row) + 1

                df.to_excel(
                    excel_writer=writer,
                    sheet_name="Sucessos",
                    startrow=row_start,
                    index=False,
                )

        # Função auxiliar para normalizar os dados
        def normalize_data(data: BotData) -> list[dict[str, str]]:
            if isinstance(data, list) and all(
                isinstance(item, dict) for item in data
            ):
                return data

            data2 = dict.fromkeys(name_colunas, "")
            for item in data:
                data2_itens = list(
                    filter(
                        lambda x: x[1] is None or str(x[1]).strip() == "",
                        list(data2.items()),
                    ),
                )
                for key, _ in data2_itens:
                    data2.update({key: item})
                    break
            return [data2]

        # Normaliza os dados para garantir formato correto
        data_to_save = normalize_data(data)

        # Salva informações na planilha de sucesso
        save_info(data_to_save, file_name_success)

        # Registra mensagem de log
        self.print_msg(message=message, type_log=type_log)

    def saudacao(self) -> Literal["Bom dia", "Boa tarde", "Boa noite"]:
        hora = datetime.now(tz=ZoneInfo("America/Manaus")).hour

        saudacao = "Boa noite"

        if 5 <= hora < 12:
            saudacao = "Bom dia"
        elif 12 <= hora < 18:
            saudacao = "Boa tarde"

        return saudacao
