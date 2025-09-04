"""Modulo de controle da classe Base para todos os bots."""

from __future__ import annotations

import json
import shutil
from contextlib import suppress
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from queue import Queue
from re import search
from threading import Event, Thread
from time import perf_counter
from typing import TYPE_CHECKING, Literal
from unicodedata import combining, normalize
from zipfile import ZIP_DEFLATED, ZipFile
from zoneinfo import ZoneInfo

import base91
from bs4 import BeautifulSoup
from humanize import precisedelta
from pandas import Timestamp, read_excel
from werkzeug.utils import secure_filename

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.main._master import AbstractCrawJUD
from crawjud.custom.task import ContextTask
from crawjud.interfaces.dict.bot import BotData, DictFiles
from crawjud.utils.storage import Storage
from crawjud.utils.webdriver import DriverBot

if TYPE_CHECKING:
    from bs4.element import PageElement

    from crawjud.interfaces.types.webdriver_types import BrowserOptions

type TypeLogs = Literal["log", "info", "success", "error"]


work_dir = Path(__file__).cwd()


class CrawJUD[T](AbstractCrawJUD, ContextTask):
    """Classe CrawJUD."""

    def __init__(
        self,
        system: str | None = None,
        selected_browser: BrowserOptions = "chrome",
    ) -> None:
        """Inicialize a instância principal do controller CrawJUD.

        Args:
            selected_browser: selected_browser
            system (str): sistema do robô

        """
        self.queue_msg = Queue()
        self.queue_files = Queue()
        self.queue_save_xlsx = Queue()
        self.event_queue_files = Event()
        self.event_queue_message = Event()
        self.event_queue_save_xlsx = Event()
        self.event_stop_bot: Event = Event()

        self.print_msg(message="Inicializando...")
        self._driver = DriverBot(
            selected_browser=selected_browser,
            with_proxy=False,
        )
        self._wait = self._driver.wait

        self.print_msg(message="Start recebido! Inicializando execução...")

        self.print_thread = Thread(
            target=self.print_in_thread,
            daemon=True,
            name="Worker Print Message",
        )

        self.thread_save_file = Thread(
            target=self.save_file,
            daemon=True,
        )

        self.print_thread.start()
        self.thread_save_file.start()

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
                out = self.output_dir_path.joinpath(file)
                with out.open("wb") as fp:
                    fp.write(file_.data)

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
        type_log: TypeLogs = "log",
    ) -> None:
        """Imprime mensagem de log do processo.

        Args:
            self: Instância do objeto.
            message (str): Mensagem a ser exibida.
            row (int): Linha do processo.
            errors (int): Quantidade de erros.
            type_log (TypeLogs): Tipo de log.

        """
        keyword_args: dict[str, str | int] = {
            "start_time": self.start_time,
            "message": message,
            "total_rows": self.total_rows,
            "row": row,
            "type_log": type_log,
            "pid": self.pid,
            "success": self.success,
            "error": self.error,
            "remaining": self.remaining,
        }

        if all(
            [
                row > 0,
                self.remaining == 0,
                "fim da execução" not in message,
            ],
        ):
            self.remaining = self.total_rows
            keyword_args.update({"remaining": self.remaining})

        if any([type_log == "success", type_log == "error"]):
            self.remaining = self.remaining - 1
            keyword_args.update({"remaining": self.remaining})

            if type_log == "success":
                self.success += 1
                keyword_args.update({"success": self.success})

            elif type_log == "error":
                self.error += 1
                keyword_args.update({"error": self.error})

        with suppress(Exception):
            self.queue_msg.put(keyword_args)

    def saudacao(self) -> Literal["Bom dia", "Boa tarde", "Boa noite"]:
        hora = datetime.now(tz=ZoneInfo("America/Manaus")).hour

        saudacao = "Boa noite"

        if 5 <= hora < 12:
            saudacao = "Bom dia"
        elif 12 <= hora < 18:
            saudacao = "Boa tarde"

        return saudacao

    def finalize_execution(self) -> None:
        """Finalize bot execution by closing browsers and logging total time.

        Performs cookie cleanup, quits the driver, and prints summary logs.
        """
        with suppress(Exception):
            window_handles = self.driver.window_handles
            if window_handles:
                self.driver.delete_all_cookies()
                self.driver.quit()

        end_time = perf_counter()

        execution_time = timedelta(seconds=float(end_time - self.start_time))
        type_log = "success"
        delta_humanized = precisedelta(
            execution_time,
            format="%0.0f",
            minimum_unit="seconds",
            suppress=["microseconds"],
        )

        message = f"Fim da execução | Tempo de Execução: {delta_humanized}"
        self.print_msg(message=message, row=self.row, type_log=type_log)

        type_log = "info"
        message = f"Sucessos: {self.success} | Erros: {self.error}"
        self.print_msg(message=message, row=self.row, type_log=type_log)

        self.thread_save_file.join()

        zip_file = self.zip_result()
        self.storage.upload_file(file_name=zip_file.name, file_path=zip_file)
        link = self.storage.get_presigned_url(
            method="GET",
            object_name=zip_file.name,
        )

        message = f"Baixe os resultados aqui: {link}"
        self.print_msg(message=message, row=self.row, type_log="info")

        self.event_queue_message.set()

    def append_error(self, *args: T, **kwargs: T) -> None:
        """Adiciona erro ao DataFrame e salva na planilha.

        Args:
            *args (T): Argumentos posicionais.
            **kwargs (T): Argumentos nomeados.

        """

    def format_string(self, string: str) -> str:
        normalized_string = "".join([
            c for c in normalize("NFKD", string) if not combining(c)
        ])

        return secure_filename(normalized_string)

    def text_is_a_date(self, text: str) -> bool:
        """Determine if the provided text matches a date-like pattern.

        Args:
            text (str): The text to evaluate.

        Returns:
            bool: True if the text resembles a date; False otherwise.

        """
        date_like_pattern = r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"
        return bool(search(date_like_pattern, text))

    def parse_data(self, inner_html: str) -> dict[str, str]:
        soup = BeautifulSoup(inner_html, "html.parser")
        dados = {}
        # percorre todas as linhas <tr>

        def normalize(txt: str) -> str:
            # Junta quebras de linha/tabs/múltiplos espaços em espaço simples
            return " ".join(txt.split())

        def get_text(td: PageElement) -> str:
            # Usa separador " " para não colar palavras; strip nas bordas
            return normalize(td.get_text(" ", strip=True))

        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            i = 0
            while i < len(tds):
                td = tds[i]
                lbl_tag = td.find("label")
                if lbl_tag:
                    label = normalize(lbl_tag.get_text().rstrip(":"))
                    # avançar para o próximo td que tenha conteúdo real (pule espaçadores)
                    j = i + 1
                    valor = ""
                    while j < len(tds):
                        texto = get_text(tds[j])
                        # considera vazio se for "&nbsp;" ou string vazia
                        if texto and texto != " ":  # &nbsp; vira U+00A0
                            valor = texto
                            break
                        j += 1
                    if label and valor and ":" not in valor:
                        dados[label] = valor
                    # continue a partir do td seguinte ao que usamos como valor
                    i = j + 1
                else:
                    i += 1

        return dados

    def zip_result(self) -> Path:
        zip_filename = f"{self.pid[:6].upper()}.zip"
        source_dir = self.output_dir_path
        output_dir = work_dir.joinpath("archives", zip_filename)

        output_dir.parent.mkdir(exist_ok=True, parents=True)

        with ZipFile(output_dir, "w", ZIP_DEFLATED) as zipfile:
            for root, _, files in source_dir.walk():
                for file in files:
                    if self.pid in file and ".log" not in file:
                        file_path = root.joinpath(file)
                        arcname = file_path.relative_to(source_dir)
                        zipfile.write(file_path, arcname)

        return output_dir
