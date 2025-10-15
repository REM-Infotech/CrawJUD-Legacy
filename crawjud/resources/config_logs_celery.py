"""Módulo Celery App do CrawJUD Automatização."""

from __future__ import annotations

import logging
import re
from logging.config import dictConfig
from os import environ, getenv
from pathlib import Path
from platform import node
from uuid import uuid4

from celery.signals import after_setup_logger
from clear import clear
from dotenv import dotenv_values
from tqdm import tqdm

from crawjud.custom import AsyncCelery as Celery
from crawjud.utils.logger import dict_config

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

    log_level = logging.INFO
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
