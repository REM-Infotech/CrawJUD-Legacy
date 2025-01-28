from __future__ import annotations

import platform
from importlib import import_module
from pathlib import Path
from time import sleep
from typing import Dict, Tuple, Union

import pandas as pd
import psutil
from billiard.context import Process
from celery import shared_task
from celery.result import AsyncResult
from flask import Flask
from openai import OpenAI

if platform.system() == "Windows":
    from pywinauto import Application

from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

__all__ = [
    "pd",
    "Application",
    "Group",
    "Live",
    "Panel",
    "Progress",
    "TaskID",
    "BarColumn",
    "DownloadColumn",
    "TextColumn",
    "TimeElapsedColumn",
    "TimeRemainingColumn",
    "TransferSpeedColumn",
    "OpenAI",
]

process_type = Union[psutil.Process, None]


# import signal
# from pathlib import Path
# from threading import Thread as Process


class BotThread(Process):

    exc_bot: Exception = None

    def join(self) -> None:
        Process.join(self)
        if self.exc_bot:
            raise self.exc_bot

    def run(self) -> None:

        self.exc_bot: Exception = None

        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e


class WorkerBot:

    system: str
    kwrgs: Dict[str, str]

    __dict__: Dict[str, str]

    @staticmethod
    @shared_task(ignore_result=False)
    def start_bot(path_args: str, display_name: str, system: str, typebot: str) -> str:

        try:
            process = BotThread(
                target=WorkerBot,
                args=(
                    path_args,
                    display_name,
                    system,
                    typebot,
                ),
            )
            process.start()
            sleep(2)
            # pid = Path(path_args).stem

            if not process.is_alive():
                try:
                    process.join()

                except Exception as e:
                    raise e

            while process.is_alive():
                ...

            else:
                process.join()

        except Exception as e:
            raise e

        return str("Finalizado!")

    # argv: str = None, botname: str = None
    def __init__(
        self,
        path_args: str,
        display_name: str,
        system: str,
        typebot: str,
        *args: Tuple[str],
        **kwargs: Dict[str, str],
    ) -> None:
        try:

            from app.run import flask_app as app

            with app.app_context():

                display_name_ = (
                    args[0] if args else kwargs.pop("display_name", display_name)
                )
                path_args_ = args[1] if args else kwargs.pop("path_args", path_args)
                system_ = args[2] if args else kwargs.pop("system", system)
                typebot_ = args[3] if args else kwargs.pop("typebot", typebot)

                kwargs.update({"display_name": display_name})

                bot_: ClassesSystems = getattr(
                    import_module(f".scripts.{system_}", __package__),
                    system_,
                )

                bot_(
                    **{
                        "display_name": display_name_,
                        "path_args": path_args_,
                        "typebot": typebot_,
                        "system": system_,
                    }
                )

        except Exception as e:
            raise e

    @classmethod
    def stop(cls, processID: int, pid: str, app: Flask = None) -> str:

        try:
            Process = AsyncResult(processID)

            print(Process.status)

            if app.testing is True or (Process and Process.status == "PENDING"):

                path_flag = (
                    Path(__file__)
                    .cwd()
                    .joinpath("exec")
                    .joinpath(pid)
                    .joinpath(f"{pid}.flag")
                    .resolve()
                )
                if not path_flag.exists():
                    path_flag.parent.mkdir(parents=True, exist_ok=True)
                    with path_flag.open("w") as f:
                        f.write("Encerrar processo")

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {processID} stopped!"

        except Exception as e:
            return str(e)

    @classmethod
    def check_status(cls, processID: str) -> str:  # pragma: no cover

        try:

            Process = AsyncResult(processID)

            status: str = Process.status
            if status == "SUCCESS":
                return f"Process {processID} stopped!"

            elif status == "FAILURE":
                return "Erro ao inicializar robô"

            return "Process running!"

        except Exception:
            return f"Process {processID} stopped!"


if __name__ == "__main__":

    from .scripts import ClassesSystems
