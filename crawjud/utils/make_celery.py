"""Celery configuration for Quart application."""

import logging
from os import getenv
from pathlib import Path

from celery import Celery
from celery.signals import setup_logging
from quart import Quart

from crawjud.types import AnyType


@setup_logging.connect()
def config_loggers(
    *args: AnyType,
    **kwargs: AnyType,
) -> None:
    """Configure logging for Celery."""
    from logging.config import dictConfig

    from crawjud.logs import log_cfg

    logger_name = f"{getenv('APPLICATION_APP')}_celery"
    log_file = Path(__file__).cwd().resolve().joinpath("logs", f"{logger_name}.log")
    log_file.touch(exist_ok=True)

    log_level = logging.INFO
    if getenv("DEBUG", "False").lower() == "True":
        log_level = logging.DEBUG

    cfg, _ = log_cfg(
        str(log_file),
        log_level,
        logger_name=logger_name.replace("_", "."),
        max_bytes=8196 * 1024,
        bkp_ct=5,
    )
    dictConfig(cfg)


async def make_celery(app: Quart) -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY"])

    class ContextTask(celery.Task):
        def __call__(
            self,
            *args: tuple,
            **kwargs: dict,
        ) -> any:  # -> any:
            return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
