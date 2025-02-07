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

# from importlib import import_module
from pathlib import Path
from time import sleep

import pandas as pd
import psutil
from celery import shared_task
from celery.result import AsyncResult
from openai import OpenAI
from quart import Quart

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
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from .class_thead import BotThread
from .scripts import caixa, calculadoras, elaw, esaj, pje, projudi

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
    "Chrome",
    "Options",
    "Service",
    "WebDriver",
    "WebDriverWait",
    "projudi",
    "esaj",
    "elaw",
    "pje",
    "calculadoras",
    "caixa",
]

process_type = psutil.Process
logger = logging.getLogger(__name__)
# import signal
# from pathlib import Path
# from threading import Thread as Process


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
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)
            process = BotThread(target=WorkerBot, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)
            # pid = Path(path_args).stem

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
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
        logger: logging.Logger = None,
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
            logger (logging.Logger, optional): The logger instance.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)
            display_name_ = args[0] if args else kwargs.pop("display_name", display_name)
            path_args_ = args[1] if args else kwargs.pop("path_args", path_args)
            system_ = args[2] if args else kwargs.pop("system", system)
            typebot_ = args[3] if args else kwargs.pop("typebot", typebot)

            kwargs.update({"display_name": display_name})

            bot_ = globals().get(system_.lower())

            bot_(display_name=display_name_, path_args=path_args_, typebot=typebot_, system=system_)

        except Exception as e:
            raise e

    @classmethod
    async def stop(cls, processID: int, pid: str, app: Quart = None) -> str:  # noqa: N803
        """Stop a process with the given processID.

        Args:
            processID (int): The process ID to stop.
            pid (str): The PID of the process.
            app (Flask, optional): The Quart app instance.

        Returns:
            str: A message indicating the stop result.

        """
        try:
            process = None
            if processID:
                process = AsyncResult(processID)
                logger.info(process.status)

            if process is None or (process and process.status == "PENDING"):
                path_flag = Path(app.config["TEMP_PATH"]).joinpath(pid).joinpath(f"{pid}.flag").resolve()
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
    async def check_status(cls, processID: str, pid: str, app: Quart) -> str:  # noqa: N803
        """Check the status of a process.

        Args:
            processID (str): The process ID to check.
            pid (str): The PID of the process.
            app (Flask): The Quart app


        Returns:
            str: A status message regarding the process.

        """
        try:
            process = AsyncResult(processID)
            path_flag = Path(app.config["TEMP_PATH"]).joinpath(pid).joinpath(f"{pid}.flag").resolve()
            status = process.status
            if status == "SUCCESS":
                return f"Process {processID} stopped!"

                if status == "FAILURE":
                    return "Erro ao inicializar robô"

            elif status == "PENDING" and path_flag.exists():
                process.revoke(terminate=True, wait=True, timeout=5.0)
                return f"Process {processID} stopped!"

            return "Process running!"

            if processID is None:
                return "Process stopped!"

        except Exception:
            return f"Process {processID} stopped!"
