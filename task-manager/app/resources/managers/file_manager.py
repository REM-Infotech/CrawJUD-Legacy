"""Gerenciador de arquivos recebidos para a execução do robô."""

from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

from dotenv import load_dotenv
from minio import Minio as MinioClient

from app.resources.formatadores import formata_string
from config import config
from constants import WORKDIR

load_dotenv()

if TYPE_CHECKING:
    from celery import Celery

    from app.bots.head import CrawJUD


class FileManager(MinioClient):
    """Gerenciador de arquivos recebidos para a execução do robô."""

    celery_app: Celery

    def __init__(self, bot: CrawJUD) -> None:
        """Inicialize o gerenciador com o bot informado.

        Args:
            bot (CrawJUD): Instância do robô principal.

        """
        dict_config = dict(list(config.as_dict().items()))
        super().__init__(
            endpoint=dict_config["MINIO_ENDPOINT"],
            access_key=dict_config.get("MINIO_ACCESS_KEY"),
            secret_key=dict_config.get("MINIO_SECRET_KEY"),
            session_token=dict_config.get("MINIO_SESSION_TOKEN"),
            secure=dict_config.get("MINIO_SECURE", False),
            region=dict_config.get("MINIO_REGION"),
            http_client=dict_config.get("MINIO_HTTP_CLIENT"),
            credentials=dict_config.get("MINIO_CREDENTIALS"),
            cert_check=dict_config.get("MINIO_CERT_CHECK", False),
        )

        self.bot = bot

    def download_files(self) -> None:
        """Baixe arquivos do Minio para o diretório de saída do robô."""
        if self.bot.config.get("folder_objeto_minio"):
            for item in self.list_objects(
                "outputexec-bots",
                prefix=self.bot.config["folder_objeto_minio"],
                recursive=True,
            ):
                file_path = str(
                    self.bot.output_dir_path.joinpath(
                        formata_string(Path(item.object_name).name),
                    ),
                )
                _obj = self.fget_object(
                    item.bucket_name,
                    item.object_name,
                    file_path,
                )

    def upload_file(self) -> str:
        """Gere e envie arquivo zip ao Minio, retornando URL.

        Returns:
            str: URL para download do arquivo zip enviado.

        """
        zipfile = self.__zip_result()

        self.fput_object("outputexec-bots", zipfile.name, str(zipfile))

        return self.get_presigned_url(
            "GET",
            "outputexec-bots",
            object_name=zipfile.name,
        )

    def __zip_result(self) -> Path:
        zip_filename = f"{self.bot.pid[:6].upper()}.zip"
        source_dir = self.bot.output_dir_path
        output_dir = WORKDIR.joinpath("archives", zip_filename)

        output_dir.parent.mkdir(exist_ok=True, parents=True)

        with ZipFile(output_dir, "w", ZIP_DEFLATED) as zipfile:
            for root, _, files in source_dir.walk():
                for file in files:
                    if self.bot.pid in file and ".log" not in file:
                        file_path = root.joinpath(file)
                        arcname = file_path.relative_to(source_dir)
                        zipfile.write(file_path, arcname)

        return output_dir
