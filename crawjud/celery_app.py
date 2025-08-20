"""Módulo Celery App do CrawJUD Automatização."""

from __future__ import annotations

import argparse
import importlib
import logging
import platform
import re
from contextlib import suppress
from logging.config import dictConfig
from multiprocessing import Process
from os import environ, getenv
from pathlib import Path
from platform import node
from sys import argv
from time import sleep
from typing import TYPE_CHECKING
from uuid import uuid4

from celery.apps.beat import Beat
from celery.apps.worker import Worker
from celery.signals import after_setup_logger
from clear import clear
from dotenv import dotenv_values
from inquirer import List, prompt
from inquirer.themes import GreenPassion
from tqdm import tqdm

from crawjud.custom import AsyncCelery as Celery
from crawjud.utils.load_config import Config
from crawjud.utils.logger import dict_config

if TYPE_CHECKING:
    from collections.abc import Callable

app = Celery(__name__)


clear()
envdot = dotenv_values()
environ["WORKER_NAME"] = f"{uuid4().hex[:5].upper()}@{node()}"

work_dir = Path(__file__).cwd()


@after_setup_logger.connect
def config_loggers[T](
    logger: logging.Logger,
    **kwargs: T,
) -> None:
    """Configure and alter the Celery logger for the application.

    This function updates the Celery logger
    configuration based on environment variables
    and custom logging settings. It ensures that
    the Celery logger uses the desired log level
    and handlers derived from the application's logging configuration.

    Args:
        logger (logging.Logger): The logger instance to configure.
        *args (AnyType): Positional arguments.
        **kwargs (AnyType): Keyword arguments, may include a
            'logger' instance to be configured.

    """
    tqdm.write(str(kwargs))
    logger_name = environ.get(
        "WORKER_NAME",
        str(re.sub(r"[^a-zA-Z0-9]", "_", "crawjud_app")),
    )
    log_path = Path().cwd().joinpath("temp", "logs")
    log_path.mkdir(exist_ok=True, parents=True)
    log_file = log_path.joinpath(f"{logger_name}.log")
    log_file.touch(exist_ok=True)

    log_level = logging.DEBUG
    if getenv("DEBUG", "False").lower() == "true":
        log_level = logging.DEBUG

    config, _ = dict_config(
        LOG_LEVEL=log_level,
        LOGGER_NAME=logger_name,
        FILELOG_PATH=log_file,
    )

    logger.handlers.clear()
    dictConfig(config)
    # Alter the Celery logger using the provided logger from kwargs if available.
    logger.setLevel(log_level)
    configured_logger = logging.getLogger(logger_name.replace("_", "."))
    for handler in configured_logger.handlers:
        logger.addHandler(handler)


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    importlib.import_module("crawjud.tasks", __package__)

    config = Config.load_config()

    app.conf.update(config.celery_config)

    app.conf.update(
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",
    )

    return app


def start_worker() -> None:
    """Start the Celery Worker."""
    environ.update({"APPLICATION_APP": "worker"})
    worker_name = environ["WORKER_NAME"]

    debug = envdot.get("DEBUG", "false").lower() == "true"
    pool_ = "prefork"
    if debug or platform.system() == "Windows":
        pool_ = "threads"

    celery = make_celery()
    worker = Worker(
        app=celery,
        hostname=worker_name,
        task_events=True,
        loglevel="INFO",
        concurrency=int(environ.get("CELERY_CONCURRENCY", "8")),
        pool=pool_,
    )
    with suppress(KeyboardInterrupt):
        worker.start()

    worker.stop()


def start_beat() -> None:
    """Start the Celery beat scheduler."""
    celery = make_celery()
    environ.update({"APPLICATION_APP": "beat"})
    scheduler = "crawjud.addons.scheduler:DatabaseScheduler"
    beat = Beat(
        app=celery,
        scheduler=scheduler,
        max_interval=5,
        loglevel="INFO",
        logfile=work_dir.joinpath(
            "temp",
            "logs",
            f"{environ['WORKER_NAME']}_beat.log",
        ),
        no_color=False,
    )
    beat.run()


def start_service(call: Callable) -> Process:
    """Crie e inicie um novo processo para executar a função fornecida como serviço.

    Args:
    call (Callable): Função a ser executada em um novo processo.

    Returns:
    Process: Instância do processo iniciado para o serviço.

    """
    proc = Process(target=call)
    proc.start()
    return proc


def restart_service(call: Callable, proc: Process) -> Process:
    """Reinicie o serviço encerrando o processo atual e iniciando um novo processo.

    Args:
        call (Callable): Função a ser executada no novo processo.
        proc (Process): Processo atual a ser encerrado.

    Returns:
        Process: Novo processo iniciado para o serviço.

    """
    stop_service(proc)
    sleep(5)

    return start_service(call)


def stop_service(proc: Process) -> bool:
    """Pare o serviço passado como processo.

    Args:
        proc (Process): Processo a ser parado.

    Returns:
        bool: True se o processo foi parado com sucesso, False caso contrário.

    """
    proc.terminate()
    proc.join()
    # Retorna True se o processo foi parado com sucesso, False caso contrário.
    return proc.is_alive()


def main() -> None:  # pragma: no cover
    """Entrada main."""
    with suppress(KeyboardInterrupt, Exception):
        calls = {"worker": start_worker, "beat": start_beat}
        args = argv[1:]

        parser = argparse.ArgumentParser("Celery App CrawJUD.")
        parser.add_argument(
            "--type",
            default="worker",
            help="Tipo de inicialização do celery (ex.: beat, worker, etc.)",
        )
        namespaces = parser.parse_args(args)

        callable_obj = calls[namespaces.type]
        process_celery = start_service(callable_obj)

        process_running = True

        opt_1 = f"Reiniciar {str(namespaces.type).capitalize()}"
        opt_2 = f"Encerrar {str(namespaces.type).capitalize()}"

        while process_running:
            clear()
            questions = [
                List(
                    "option_server",
                    "Selecione o que fazer",
                    choices=[
                        opt_1,
                        opt_2,
                    ],
                    default=opt_1,
                ),
            ]

            result = prompt(questions, theme=GreenPassion())

            if not result:
                process_running = stop_service(process_celery)
                break

            if result.get("option_server") == opt_1:
                process_celery = restart_service(callable_obj, process_celery)

            elif result.get("option_server") == opt_2:
                process_running = stop_service(process_celery)

    clear()
    tqdm.write("Serviço encerrado!")
