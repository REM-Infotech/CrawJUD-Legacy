"""Modulo de controle da classe Base para todos os bots."""

from __future__ import annotations

import json
import shutil
import traceback
from contextlib import suppress
from datetime import datetime
from io import BytesIO
from pathlib import Path
from queue import Queue
from re import search
from threading import Event, Thread
from time import perf_counter, sleep
from typing import TYPE_CHECKING, Literal
from unicodedata import combining, normalize
from uuid import uuid4
from zoneinfo import ZoneInfo

import base91
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, Timestamp, read_excel
from socketio import Client
from termcolor import colored
from tqdm import tqdm
from werkzeug.utils import secure_filename

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.abstract import AbstractCrawJUD
from crawjud.custom.task import ContextTask
from crawjud.interfaces.dict.bot import BotData, DictFiles
from crawjud.utils.models.logs import MessageLogDict
from crawjud.utils.storage import Storage
from crawjud.utils.webdriver import DriverBot

if TYPE_CHECKING:
    from bs4.element import PageElement

func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}

work_dir = Path(__file__).cwd()

COLORS_DICT = {
    "info": "cyan",
    "log": "white",
    "error": "red",
    "warning": "magenta",
    "success": "green",
}


class CrawJUD[T](AbstractCrawJUD, ContextTask):
    """Classe CrawJUD."""

    event_stop_bot: Event
    queue_msg = Queue()

    def __init__(self, system: str | None = None) -> None:
        """Inicialize a instância principal do controller CrawJUD.

        Args:
            self: Self@CrawJUD[T@CrawJUD]: Instância do objeto.
            system (str): sistema do robô

        """
        self.event_stop_bot: Event = Event()
        if system != "pje":
            self._driver = DriverBot(
                selected_browser="chrome",
                with_proxy=False,
            )
            self._wait = self._driver.wait

        Thread(
            target=self.print_in_thread,
            daemon=True,
            name="Worker Print Message",
        ).start()

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
            tqdm.write(str(args))
            tqdm.write(str(kwargs))
            tqdm.write("teste")
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
                    pid: str | None = data.get("pid", uuid4().hex)

                    with suppress(Exception):
                        sio.emit(
                            event="join_room",
                            data={"data": {"room": self.pid}},
                            namespace=namespace,
                        )

                    # Formata o horário atual
                    time_exec = current_time.strftime("%H:%M:%S")

                    # Obtém o PID reduzido
                    mini_pid = pid[:6].upper()

                    # Monta o prompt da mensagem
                    message = f"[({mini_pid}, {type_log}, {row}, {time_exec})> {message}]"

                    # Cria objeto de log da mensagem
                    data = {
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
                            start_time=start_time,
                        ),
                    }

                    # Envia o log da execução
                    with suppress(Exception):
                        sio.emit(
                            event="log_execution",
                            data=data,
                            namespace=namespace,
                        )

                    # Cria o caminho do arquivo de log
                    file_log_name = f"{pid[:4].upper()}.log"
                    file_log = work_dir.joinpath("temp", pid, file_log_name)

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

                # Finaliza a tarefa da fila
                self.queue_msg.task_done()

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

    def save_file(self) -> None:
        """Consome itens da fila `queue_save_xlsx` e adiciona na planilha.

        Encerra quando receber o sentinela (None).

        """
        nome_planilha = f"Planilha Resultados - {self.pid}.xlsx"
        path_planilha = self.output_dir_path.joinpath(nome_planilha)

        # cria/abre arquivo para APPEND
        # pandas >= 2.0: if_sheet_exists=('replace'|'overlay'|'new'), funciona só em mode='a'
        while (
            not self.event_queue_save_xlsx.is_set()
            and not self.event_stop_bot.is_set()
        ):
            data = self.queue_save_xlsx.get()
            try:
                sleep(2)
                rows = data["to_save"]
                sheet_name = data["sheet_name"]

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
                tqdm.write(f"Salvando worksheet: {sheet_name}")
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
                            writer,
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
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                sleep(2)
                tqdm.write("Worksheet salvo!")
            except Exception as e:
                # logue o stack completo (não interrompe o consumidor)
                tqdm.write("\n".join(traceback.format_exception(e)))

            finally:
                sleep(2)
                self.queue_save_xlsx.task_done()
                tqdm.write(
                    f"Fim da tarefa. Restantes {self.queue_save_xlsx.unfinished_tasks}",
                )

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
        execution_time = datetime.fromtimestamp(
            end_time - self.start_time,
            tz=ZoneInfo("America/Manaus"),
        )

        type_log = "success"
        message = f"Fim da execução | Tempo de Execução: {execution_time.strftime('%H:%M:%S')}"
        self.print_msg(message=message, row=self.row, type_log=type_log)

        type_log = "info"
        message = f"Sucessos: {self.success} | Erros: {self.error}"
        self.print_msg(message=message, row=self.row, type_log=type_log)

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
                    if label and valor:
                        dados[label] = valor
                    # continue a partir do td seguinte ao que usamos como valor
                    i = j + 1
                else:
                    i += 1

        return dados
