"""
Package for CrawJUD-Bots, a web scraper and bot for automated interaction with the Brazilian Justice System.

Subpackages:
    core: Core functions for CrawJUD-Bots.
    shared: Shared functions and classes between packages.
    Utils: Utility functions and classes for CrawJUD-Bots.
    common: Common functions and classes for CrawJUD-Bots.
    scripts: Scripts for CrawJUD-Bots.

Modules:
    __init__: Initialization module for the CrawJUD-Bots package.
    core: Core functions for CrawJUD-Bots.
    shared: Shared functions and classes between packages.
    Utils: Utility functions and classes for CrawJUD-Bots.
    common: Common functions and classes for CrawJUD-Bots.
    scripts: Scripts for CrawJUD-Bots.
"""

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
        """
        Wait for the BotThread to finish its execution.

        This method overrides the `join` method of the `Process` class.
        It waits for the thread to complete its execution. If an exception
        occurred during the execution of the thread, it raises that exception.
        """
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
        """
        Inicia um novo processo de um rob  com base em um conjunto de argumentos.

        Args:
            path_args (str): Caminho para o arquivo json com argumentos do rob .
            display_name (str): Nome do rob  para ser exibido na interface de controle.
            system (str): Sistema do rob  (projudi, pje, elaw, caixa, etc.).
            typebot (str): Tipo do rob  (capa, movimenta o, proc parte, etc.).

        Returns:
            str: Status do rob  (Finalizado!).
        """
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
        """
        Initialize a WorkerBot instance with specified parameters.

        This constructor sets up a WorkerBot instance, importing the necessary bot
        module based on the specified system and executing the bot with the provided
        arguments.

        Args:
            path_args (str): The path to the arguments file for the bot.
            display_name (str): The display name for the bot.
            system (str): The system for which the bot is being initialized.
            typebot (str): The type of bot being executed.
            *args (Tuple[str]): Additional positional arguments.
            **kwargs (Dict[str, str]): Additional keyword arguments.

        Raises:
            Exception: If an error occurs during the bot's initialization or execution.
        """
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
        """
        Stop a process with the given processID and return a message accordingly.

        Args:
            processID (int): The process ID of the process to be stopped.
            pid (str): The PID of the process to be stopped.
            app (Flask, optional): The Flask app instance. Defaults to None.

        Returns:
            str: A message indicating whether the process was stopped or not.
        """
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
