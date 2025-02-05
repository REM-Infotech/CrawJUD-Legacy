"""Package: CrawJUD-Bots.

CrawJUD-Bots is a web scraper and bot for automated interaction with the
Brazilian Justice System.

Subpackages:
    core: Core functions for CrawJUD-Bots.
    shared: Shared functions and classes.
    Utils: Utility functions and classes.
    common: Common functions and classes.
    scripts: Scripts for CrawJUD-Bots.

Modules:
    __init__: Initialization of the CrawJUD-Bots package.
    core, shared, Utils, common, scripts: Other modules.
"""

from __future__ import annotations

import logging
import platform
from importlib import import_module
from pathlib import Path
from time import sleep

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
    "Application",
    "BarColumn",
    "DownloadColumn",
    "Group",
    "Live",
    "OpenAI",
    "Panel",
    "Progress",
    "TaskID",
    "TextColumn",
    "TimeElapsedColumn",
    "TimeRemainingColumn",
    "TransferSpeedColumn",
    "pd",
]

process_type = psutil.Process
logger = logging.getLogger(__name__)
# import signal
# from pathlib import Path
# from threading import Thread as Process


class BotThread(Process):
    """A BotThread that extends Process to handle bot execution.

    Attributes:
        exc_bot (Exception): Stores any exception raised during execution.

    """

    exc_bot: Exception = None

    def join(self) -> None:
        """Wait for the BotThread to finish execution.

        If an exception occurred during execution, it is raised.
        """
        Process.join(self)
        if self.exc_bot:
            raise self.exc_bot

    def run(self) -> None:
        """Run the target function in the BotThread.

        Captures any exceptions raised during execution.
        """
        self.exc_bot = None

        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e


class WorkerBot:
    """Manage the lifecycle of bot processes.

    Attributes:
        system (str): The operating system.
        kwrgs (dict[str, str]): Keyword arguments for bot configuration.

    """

    system: str
    kwrgs: dict[str, str]
    __dict__: dict[str, str]

    @staticmethod
    @shared_task(ignore_result=False)
    def start_bot(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        try:
            process = BotThread(target=WorkerBot, args=(path_args, display_name, system, typebot))
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
        *args: tuple[str],
        **kwargs: dict[str, str],
    ) -> None:
        """Initialize a WorkerBot instance.

        Sets up the bot and executes the bot module based on the system type.

        Args:
            path_args (str): Path to the bot's arguments file.
            display_name (str): The display name for the bot.
            system (str): The system for the bot (e.g., projudi).
            typebot (str): The type of bot (e.g., capa).
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        try:
            from app.run import flask_app as app

            with app.app_context():
                display_name_ = args[0] if args else kwargs.pop("display_name", display_name)
                path_args_ = args[1] if args else kwargs.pop("path_args", path_args)
                system_ = args[2] if args else kwargs.pop("system", system)
                typebot_ = args[3] if args else kwargs.pop("typebot", typebot)

                kwargs.update({"display_name": display_name})

                bot_ = getattr(import_module(f".scripts.{system_}", __package__), system_.lower())

                bot_(display_name=display_name_, path_args=path_args_, typebot=typebot_, system=system_)

        except Exception as e:
            raise e

    @classmethod
    def stop(cls, processID: int, pid: str, app: Flask = None) -> str:  # noqa: N803
        """Stop a process with the given processID.

        Args:
            processID (int): The process ID to stop.
            pid (str): The PID of the process.
            app (Flask, optional): The Flask app instance.

        Returns:
            str: A message indicating the stop result.

        """
        try:
            process = AsyncResult(processID)

            logger.info(process.status)

            if (app and app.testing) or (process and process.status == "PENDING"):
                path_flag = Path(__file__).cwd().joinpath("exec").joinpath(pid).joinpath(f"{pid}.flag").resolve()
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
    def check_status(cls, processID: str) -> str:  # noqa: N803
        """Check the status of a process.

        Args:
            processID (str): The process ID to check.

        Returns:
            str: A status message regarding the process.

        """
        try:
            process = AsyncResult(processID)

            status = process.status
            if status == "SUCCESS":
                return f"Process {processID} stopped!"

            if status == "FAILURE":
                return "Erro ao inicializar robô"

            return "Process running!"

        except Exception:
            return f"Process {processID} stopped!"
