"""Serviço de domínio para manipulação de arquivos e sessões."""

from __future__ import annotations

import io
import traceback
from os import remove
from pathlib import Path
from typing import AnyStr, NoReturn

import aiofiles
from clear import clear
from crawjud.resources import format_string
from crawjud.utils.storage import Storage
from quart import request, session
from tqdm import tqdm
from werkzeug.datastructures import FileStorage

workdir_path = Path(__file__).cwd()


class ChunkIncompletoError(ValueError):
    """Exceção para chunks de arquivo incompletos durante upload.

    Utilizada para sinalizar falhas em uploads parciais.
    """

    message: str

    def __init__(self, message: str, *args) -> None:
        """Inicialize a exceção de chunk incompleto.

        Args:
            self: Instância do objeto.
            message (str): Mensagem de erro.
            *args: Argumentos adicionais.

        """
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        """Empty.

        Returns:
            str: string

        """
        return self.message


class UploadFileError(Exception):
    """Exceção para falhas no upload de arquivos.

    Utilizada para sinalizar erros durante o upload.
    """

    message: str

    def __init__(self, message: str, *args) -> None:
        """Inicialize a exceção de erro de upload de arquivo.

        Args:
            self: Instância do objeto.
            message (str): Mensagem de erro.
            *args: Argumentos adicionais.

        """
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        """Empty.

        Returns:
            str: string

        """
        return self.message


def _raise_val_err() -> NoReturn:
    raise ChunkIncompletoError(message="Dados do chunk incompletos.")


class FileService[T]:
    """Serviço de domínio para manipulação de arquivos e sessões de usuário."""

    async def save_file(self) -> None:
        """Salva um arquivo enviado para o diretório temporário especificado."""
        storage = Storage("minio")

        try:
            data = await request.form
            file_ = await request.files
            sid = str(session.sid)

            if not data:
                data = request.socket_data
                file_ = request.socket_data

            file_name = format_string(str(data.get("name")))
            index = int(data.get("index", 0))

            _total = int(data.get("total", 1)) * 1024
            chunk = data.get("chunk", file_.get("chunk", b""))
            chunksize = int(data.get("chunksize", 1024))
            file_size = int(data.get("file_size"))
            if isinstance(chunk, FileStorage):
                chunk = chunk.stream.read()

            start_ = index * chunksize
            end_ = min(file_size, start_ + chunksize)

            content_type = str(data.get("content_type"))

            if not all([file_name, chunk, content_type]):
                tqdm.write(f"chunk: {chunk}")
                if chunk == b"":
                    return

                _raise_val_err()

            # Define diretório temporário para armazenar os chunks
            path_temp = Path(__file__).cwd().joinpath("temp")
            path_temp.mkdir(parents=True, exist_ok=True)
            file_path = path_temp.joinpath(file_name)

            # Salva o chunk no arquivo temporário
            mode = "ab" if index > 0 else "wb"

            async with aiofiles.open(file_path, mode) as f:
                await f.write(chunk)

            if end_ >= file_size:
                async with aiofiles.open(file_path, "rb") as f:
                    b_data = await f.read()
                    data_ = io.BytesIO(b_data)

                    dest_path = str(
                        Path(sid.upper())
                        .joinpath(format_string(file_name))
                        .as_posix(),
                    )
                    storage.put_object(
                        object_name=dest_path,
                        data=data_,
                        length=len(b_data),
                        content_type=content_type,
                    )

                remove(file_path)

        except (UploadFileError, OSError) as e:
            clear()
            tqdm.write("\n".join(traceback.format_exception(e)))

    async def save_session(
        self,
        server: T,
        sid: str,
        session: dict[str, AnyStr],
        namespace: str | None = None,
    ) -> None:
        """Armazena a sessão do usuário para um cliente na sessão do engineio."""
        namespace = namespace or "/"
        eio_sid = server.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await server.eio.get_session(eio_sid)
        eio_session[namespace] = session
