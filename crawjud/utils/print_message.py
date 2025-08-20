"""Print Message."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from dotenv import dotenv_values
from socketio import Client
from termcolor import colored
from tqdm import tqdm

from crawjud.utils.models.logs import MessageLogDict

if TYPE_CHECKING:
    from multiprocessing.synchronize import Lock as LockProcess

environ = dotenv_values()
work_dir = Path(__file__).cwd()
server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


def print_in_thread(
    locker: LockProcess,
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
        locker (Lock): locker
        start_time (str): Horário de início do processamento.
        message (str): Mensagem a ser registrada.
        total_rows (int): Total de linhas a serem processadas.
        row (int): Linha atual do processamento.
        errors (int): Quantidade de erros.
        type_log (str): Tipo de log (info, error, etc).
        pid (str | None): Identificador do processo.

    """
    with locker:
        sleep(5)
        sio = Client(logger=True)
        sio.connect(
            url=server,
            namespaces=[namespace],
            transports=transports,
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
        message = (
            f"[({pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"
        )
        # Monta o prompt da mensagem
        # Cria objeto de log da mensagem
        data = {
            "data": MessageLogDict(
                message=str(message),
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
                    message,
                    color={
                        "info": "cyan",
                        "log": "white",
                        "error": "red",
                        "warning": "magenta",
                        "success": "green",
                    }.get(type_log, "white"),
                ),
            )
        sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start_time",
        type=str,
        required=True,
        help="Horário de início do processamento.",
    )
    parser.add_argument(
        "--message",
        type=str,
        required=True,
        help="Mensagem a ser registrada.",
    )
    parser.add_argument(
        "--total_rows",
        type=int,
        default=0,
        help="Total de linhas a serem processadas.",
    )
    parser.add_argument(
        "--row",
        type=int,
        default=0,
        help="Linha atual do processamento.",
    )
    parser.add_argument(
        "--errors",
        type=int,
        default=0,
        help="Quantidade de erros.",
    )
    parser.add_argument(
        "--type_log",
        type=str,
        default="log",
        help="Tipo de log (info, error, etc).",
    )
    parser.add_argument("--pid", type=str, help="Identificador do processo.")

    args = parser.parse_args(sys.argv[1:])

    print_in_thread(
        start_time=args.start_time,
        message=args.message,
        total_rows=args.total_rows,
        row=args.row,
        errors=args.errors,
        type_log=args.type_log,
        pid=args.pid,
    )
