"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Event
from zipfile import ZIP_DEFLATED, ZipFile

from pandas import DataFrame, Timestamp, read_excel
from resources import format_string
from resources._minio import Minio
from resources.queues.file_operation import SaveError, SaveSuccess
from resources.queues.print_message import PrintMessage

import _hook
from __types import AnyType, T
from _interfaces import BotData, ColorsDict
from constants import WORKDIR
from controllers._crawjud import HeadCrawJUD

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


class CrawJUD(HeadCrawJUD):
    """Classe CrawJUD."""

    def __init__(self) -> None:
        """Inicializa o CrawJUD."""
        self._task = self.run
        self.run = self.__call__

    def __call__(self) -> T:
        self._bot_stopped = Event()
        self.print_message = PrintMessage()
        self.append_succes = SaveSuccess()
        self.append_error = SaveError()

        self.setup()

        return self._task()

    def setup(self) -> None:
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

    @abstractmethod
    def auth(self) -> bool:
        """Autenticação no sistema."""
        ...
