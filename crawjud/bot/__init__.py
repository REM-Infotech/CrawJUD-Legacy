"""Provide automation tools for interacting with Brazilian Justice System websites.

This module contains the core components for automating interactions with various
Brazilian Justice System websites including Projudi, PJe, eSaj and more.

The package uses Selenium for web automation and provides a task-based architecture
using Celery for managing concurrent bot operations.

Attributes:
    logger: Module level logger instance.

Classes:
    WorkerBot: Main class for managing bot lifecycle and operations.

"""

# pragma: no cover
from __future__ import annotations

import logging
import shutil
import zipfile
from os import getcwd, remove

# from importlib import import_module
from pathlib import Path
from time import sleep

from celery import shared_task
from celery.result import AsyncResult
from google.cloud.storage import Blob
from quart import Quart

from crawjud.bot.class_thead import BotThread
from crawjud.bot.common.exceptions import StartError
from crawjud.misc import bucket_gcs, storage_client

logger = logging.getLogger(__name__)


class WorkerBot:
    """Manage the lifecycle and execution of automated judicial system bots.

    This class provides methods to launch, monitor and control bot processes that interact
    with different judicial systems. It handles process lifecycle management and provides
    status monitoring capabilities.

    Attributes:
        system (str): Operating system identifier.
        kwargs (dict[str, str]): Configuration parameters for bot initialization.

    Note:
        All launcher methods are decorated with @shared_task for Celery integration.

    """

    system: str
    kwargs: dict[str, str]
    __dict__: dict[str, str]

    @classmethod
    def unzip_file(cls, zip_name: Path) -> None:
        """Extract a ZIP file into a subfolder with the same name."""
        path = zip_name.parent.resolve().joinpath(zip_name.name.split(".")[0])
        unziped_tmp_folder = Path(getcwd()).joinpath(path.name)
        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            # Extract each file directly into the subfolder
            for member in zip_ref.namelist():
                # Get the original file name without any directory structure
                dir_name = path.name
                extracted_path = Path(zip_ref.extract(member, dir_name))
                # base_name = extracted_path.name
                # If the extracted path has directories, move the file directly into the subfolder
                # chk = base_name and extracted_path.is_dir()
                # if chk:
                #     continue

                if not Path(path).joinpath(member).exists():
                    shutil.move(extracted_path, path)

        if unziped_tmp_folder.exists():
            shutil.rmtree(unziped_tmp_folder)

    @classmethod
    def download_file_gcs(cls, path_pid: Path) -> str:
        """Download a file from Google Cloud Storage (GCS).

        Args:
            path_pid (Path): Path to the file to download.
            app (Quart): Quart application instance for configuration access.

        Returns:
            str: Message indicating download completion.

        """
        path_pid = Path(path_pid).parent.resolve()
        path_pid.parent.mkdir(parents=True, exist_ok=True)

        pid = path_pid.name

        bucket = bucket_gcs(storage_client(), bucket_name="task_files_celery")

        zipped_args = ""

        # blob: list[Blob] = list(filter(lambda x: pid in blob.name, blobs))
        for blob in bucket.list_blobs():
            file_: Blob = blob

            if pid in file_.name:
                file_.download_to_filename(path_pid.with_suffix(".zip"))
                zipped_args = path_pid.with_suffix(".zip")
                break

        if zipped_args == "":
            raise StartError(message="Arquivo não encontrado no Storage")
        cls.unzip_file(zipped_args)

        remove(zipped_args)

        return "Arquivo de execução baixado com sucesso!"

    @staticmethod
    @shared_task(ignore_result=False)
    def projudi_launcher(
        *args: str | int,
        **kwargs: str | int,
    ) -> str:
        """Launch a new Projudi bot process with specified configuration.

        Creates and manages a new bot process for interacting with the Projudi system.
        Handles process lifecycle and ensures proper cleanup.

        Args:
            *args: Variable length argument list containing bot parameters.
            **kwargs: Keyword arguments including:
                path_args (str): Path to JSON configuration file.
                display_name (str): Human readable bot identifier.
                system (str): Target system identifier.
                typebot (str): Bot execution type/mode.

        Returns:
            str: Status message indicating completion ("Finalizado").

        Raises:
            Exception: If bot initialization or execution fails.

        """
        from crawjud.bot.scripts import Projudi

        bot_class = Projudi
        try:
            WorkerBot.download_file_gcs(kwargs.get("path_args"))
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=bot_class, args=args, kwargs=kwargs)
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
    def esaj_launcher(
        *args: str | int,
        **kwargs: str | int,
    ) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.


        Returns:
            str: Status message indicating bot completion.

        """
        from crawjud.bot.scripts import Esaj

        bot_class = Esaj
        try:
            WorkerBot.download_file_gcs(kwargs.get("path_args"))
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=bot_class, args=args, kwargs=kwargs)
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
    def pje_launcher(
        *args: str | int,
        **kwargs: str | int,
    ) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.


        Returns:
            str: Status message indicating bot completion.

        """
        from crawjud.bot.scripts import PJe

        bot_class = PJe
        try:
            WorkerBot.download_file_gcs(kwargs.get("path_args"))
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=bot_class, args=args, kwargs=kwargs)
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
    def elaw_launcher(
        *args: str | int,
        **kwargs: str | int,
    ) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.


        Returns:
            str: Status message indicating bot completion.

        """
        from crawjud.bot.scripts import Elaw

        bot_class = Elaw
        try:
            WorkerBot.download_file_gcs(kwargs.get("path_args"))
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=bot_class, args=args, kwargs=kwargs)
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
    def caixa_launcher(
        *args: str | int,
        **kwargs: str | int,
    ) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.


        Returns:
            str: Status message indicating bot completion.

        """
        from crawjud.bot.scripts import Caixa

        bot_class = Caixa
        try:
            WorkerBot.download_file_gcs(kwargs.get("path_args"))
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=bot_class, args=args, kwargs=kwargs)
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
    def calculadoras_launcher(
        *args: str | int,
        **kwargs: str | int,
    ) -> str:
        """Start a new bot process with the provided arguments.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.
            path_args (str): Path to the JSON file with bot arguments.
            display_name (str): Display name for the bot.
            system (str): The system for which the bot is initialized.
            typebot (str): type of bot execution.


        Returns:
            str: Status message indicating bot completion.

        """
        from crawjud.bot.scripts import Calculadoras

        bot_class = Calculadoras
        try:
            WorkerBot.download_file_gcs(kwargs.get("path_args"))
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            process = BotThread(target=bot_class, args=args, kwargs=kwargs)
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
        """Stop a running bot process gracefully.

        Attempts to stop a bot process using either task_id or process ID. Creates a flag
        file to signal the process to terminate if direct task termination is not possible.

        Args:
            task_id (int): Celery task identifier.
            pid (str): Process identifier string.
            app (Quart, optional): Quart application instance for config access.

        Returns:
            str: Message indicating stop result.

        Raises:
            Exception: If process termination fails.

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

        except Exception as e:
            return str(e)

    @classmethod
    async def check_status(cls, task_id: str, pid: str, app: Quart) -> str:
        """Check the current status of a bot process.

        Verifies the state of a bot process through multiple methods including Celery
        task status and flag file presence. Can trigger process termination if needed.

        Args:
            task_id (str): Celery task identifier.
            pid (str): Process identifier string.
            app (Quart): Quart application instance for config and logging.

        Returns:
            str: Current status message of the process.

        Note:
            Status messages include: "Process running!", "Process stopped!",
            or error messages.

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

                    if status == "PENDING" and path_flag.exists():
                        process.revoke(wait=True, signal="SIGTERM", timeout=5)
                        return f"Process {task_id} stopped!"

            except Exception as e:
                app.logger.exception("An error occurred: %s", str(e))
                process = None

            if process is None:
                path_flag.parent.resolve().mkdir(parents=True, exist_ok=True)

                with path_flag.open("w") as f:
                    f.write("Encerrar processo")

                return "Process stopped!"

            return "Process running!"

        except Exception:
            return f"Process {task_id} stopped!"
