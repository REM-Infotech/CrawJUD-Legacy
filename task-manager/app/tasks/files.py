"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

import shutil
from contextlib import suppress
from os import environ
from pathlib import Path

import pandas as pd
from celery.result import AsyncResult
from clear import clear

from app.custom.task import ContextTask
from app.decorators import shared_task
from app.resources import format_string
from app.utils.models.logs import CachedExecution
from app.utils.storage import Storage

workdir_path = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]


@shared_task(name="save_success", bind=True, base=ContextTask)
class SaveSuccessTask(ContextTask):
    """Gerencia a tarefa de salvar resultados em Excel e realizar upload.

    Args:
        pid (str): Identificador do processo de execução.
        filename (str): Nome do arquivo a ser salvo.

    Returns:
        None: Não retorna valor.

    Raises:
        FileNotFoundError: Caso o diretório de destino não exista.

    """

    def __init__(
        self,
        pid: str,
        file_name: str,
    ) -> None:
        """Inicializa a tarefa SaveSuccessTask com o PID e nome do arquivo.

        Args:
            pid (str): Identificador do processo de execução.
            file_name (str): Nome do arquivo a ser salvo.

        """
        data_query_ = CachedExecution.find(CachedExecution.pid == pid).all()

        list_data = []
        for item in data_query_:
            list_data.extend(item.data)

        storage = Storage("minio")
        path_planilha = workdir_path.joinpath("temp", pid, file_name)

        path_planilha.parent.mkdir(exist_ok=True, parents=True)
        df = pd.DataFrame(list_data)

        with pd.ExcelWriter(path_planilha, engine="openpyxl") as writter:
            df.to_excel(
                excel_writer=writter,
                index=False,
                sheet_name="Resultados",
            )

        file_name = format_string(path_planilha.name)
        storage.upload_file(f"{pid}/{file_name}", path_planilha)


@shared_task(name="clear_cache")
def clear_cache() -> None:  # noqa: D103
    from app.app_celery import app

    clear()
    temp_dir = Path(__file__).cwd().joinpath("temp")

    for root, dirs, _ in temp_dir.walk():
        for dir_ in dirs:
            path_task = root.joinpath(dir_)
            if ".wdm" in str(path_task) or "logs" in str(path_task):
                continue
            tsk = AsyncResult(dir_, app=app)

            if tsk.ready():
                continue

            with suppress(Exception):
                shutil.rmtree(path_task)
