"""
Package: CrawJUD-Bots.

CrawJUD-Bots is a web scraper and bot for automated interaction with the Brazilian Justice System.

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
    """
    The BotThread class extends Process to handle bot execution in a separate thread.

    Attributes:
        exc_bot (Exception): Stores any exception raised during bot execution.
    """

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
        """
        Run the target function in the BotThread.

        Captures any exceptions raised during execution.
        """
        self.exc_bot = None

        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e


class WorkerBot:
    """
    The WorkerBot class manages the lifecycle of bot processes.

    Attributes:
        system (str): The operating system.
        kwrgs (Dict[str, str]): Keyword arguments for bot configuration.
    """

    system: str
    kwrgs: Dict[str, str]

    __dict__: Dict[str, str]

    @staticmethod
    @shared_task(ignore_result=False)
    def start_bot(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """
        Start a new bot process based on the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot in the control interface.
            system (str): System for which the bot is initialized (projudi, pje, elaw, etc.).
            typebot (str): Type of bot to execute (capa, movimenta, proc parte, etc.).

        Returns:
            str: Status message indicating bot completion.

        Raises:
            Exception: If an error occurs during bot initialization or execution.
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
                pass

            else:
                process.join()

        except Exception as e:
            raise e

        return "Finalizado!"

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

                bot_ = getattr(
                    import_module(f".scripts.{system_}", __package__),
                    system_.lower(),
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
        Stop a process with the given processID.

        Args:
            processID (int): The process ID of the process to be stopped.
            pid (str): The PID of the process to be stopped.
            app (Flask, optional): The Flask app instance. Defaults to None.

        Returns:
            str: Message indicating the result of the stop operation.
        """
        try:
            process = AsyncResult(processID)

            print(process.status)

            if app and app.testing or (process and process.status == "PENDING"):
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
    def check_status(cls, processID: str) -> str:
        """
        Check the status of a process.

        Args:
            processID (str): The process ID to check.

        Returns:
            str: Status message of the process.
        """
        try:
            process = AsyncResult(processID)

            status = process.status
            if status == "SUCCESS":
                return f"Process {processID} stopped!"

            elif status == "FAILURE":
                return "Erro ao inicializar robô"

            return "Process running!"

        except Exception:
            return f"Process {processID} stopped!"
