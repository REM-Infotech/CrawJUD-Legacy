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
        kwargs (dict[str, str]): Keyword arguments for bot configuration.

    """

    system: str
    kwargs: dict[str, str]
    __dict__: dict[str, str]

    @staticmethod
    @shared_task(ignore_result=False)
    def projudi_launcher(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        from .scripts import Projudi

        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=Projudi, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
            process.join()

        except Exception as e:
            raise e

        return "Finalizado"

    @staticmethod
    @shared_task(ignore_result=False)
    def esaj_launcher(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        from .scripts import Esaj

        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=Esaj, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
            process.join()

        except Exception as e:
            raise e

        return "Finalizado"

    @staticmethod
    @shared_task(ignore_result=False)
    def pje_launcher(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        from .scripts import PJe

        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=PJe, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
            process.join()

        except Exception as e:
            raise e

        return "Finalizado"

    @staticmethod
    @shared_task(ignore_result=False)
    def elaw_launcher(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        from .scripts import Elaw

        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=Elaw, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
            process.join()

        except Exception as e:
            raise e

        return "Finalizado"

    @staticmethod
    @shared_task(ignore_result=False)
    def caixa_launcher(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        from .scripts import Caixa

        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=Caixa, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
            process.join()

        except Exception as e:
            raise e

        return "Finalizado"

    @staticmethod
    @shared_task(ignore_result=False)
    def calculadoras_launcher(path_args: str, display_name: str, system: str, typebot: str) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.

        Returns:
            str: Status message indicating bot completion.

        """
        from .scripts import Calculadoras

        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=Calculadoras, args=(path_args, display_name, system, typebot, logger))
            process.daemon = True
            process.start()
            sleep(2)

            if not process.is_alive():
                try:
                    process.join()
                except Exception as e:
                    raise e
            process.join()

        except Exception as e:
            raise e

        return "Finalizado"

    @classmethod
    async def stop(cls, task_id: int, pid: str, app: Quart = None) -> str:
        """Stop a process with the given task_id.

        Args:
            task_id (int): The process ID to stop.
            pid (str): The PID of the process.
            app (Flask, optional): The Quart app instance.

        Returns:
            str: A message indicating the stop result.

        """
        try:
            process = None
            if task_id:
                process = AsyncResult(task_id)
                logger.info(process.status)

            if process is None or (process and process.status == "PENDING"):
                path_flag = Path(app.config["TEMP_PATH"]).joinpath(pid).joinpath(f"{pid}.flag").resolve()
                path_flag.parent.mkdir(parents=True, exist_ok=True)
                with path_flag.open("w") as f:
                    f.write("Encerrar processo")

            return f"Process {task_id} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {task_id} stopped!"

        except Exception as e:
            return str(e)

    @classmethod
    async def check_status(cls, task_id: str, pid: str, app: Quart) -> str:
        """Check the status of a process.

        Args:
            task_id (str): The process ID to check.
            pid (str): The PID of the process.
            app (Flask): The Quart app


        Returns:
            str: A status message regarding the process.

        """
        try:
            path_flag = Path(app.config["TEMP_PATH"]).joinpath(pid).joinpath(f"{pid}.flag").resolve()
            process = None
            try:
                if task_id:
                    process = AsyncResult(task_id)
                    status = process.status
                    if status == "SUCCESS":
                        return f"Process {task_id} stopped!"

                    if status == "FAILURE":
                        return "Erro ao inicializar robô"

                    elif status == "PENDING" and path_flag.exists():
                        process.revoke(wait=True, signal="SIGTERM")
                        return f"Process {task_id} stopped!"

            except Exception as e:
                app.logger.error("An error occurred: %s", str(e))
                process = None

            if process is None:
                path_flag.parent.resolve().mkdir(parents=True, exist_ok=True)

                with path_flag.open("w") as f:
                    f.write("Encerrar processo")

                return "Process stopped!"

            return "Process running!"

        except Exception:
            return f"Process {task_id} stopped!"
