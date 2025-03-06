"""Celery configuration for Quart application."""

import logging  # noqa: F401
from os import getenv  # noqa: F401
from pathlib import Path  # noqa: F401

from celery import Celery
from celery.signals import after_setup_logger  # noqa: F401
from quart import Quart

from crawjud.types import AnyType  # noqa: F401


@after_setup_logger.connect
def config_loggers(
    logger: logging.Logger,
    *args: AnyType,
    **kwargs: AnyType,
) -> None:
    """Configure and alter the Celery logger for the application.

    This function updates the Celery logger configuration based on environment
    variables and custom logging settings. It ensures that the Celery logger uses
    the desired log level and handlers derived from the application's logging configuration.

    Args:
        logger (logging.Logger): The logger instance to configure.
        *args (AnyType): Positional arguments.
        **kwargs (AnyType): Keyword arguments, may include a 'logger' instance to be configured.

    """
    from logging.config import dictConfig

    from crawjud.logs import log_cfg

    logger_name = f"{getenv('APPLICATION_APP')}_celery"
    log_file = Path(__file__).cwd().resolve().joinpath("crawjud", "logs", f"{logger_name}.log")
    log_file.touch(exist_ok=True)

    log_level = logging.INFO
    if getenv("DEBUG", "False").lower() == "true":
        log_level = logging.DEBUG

    cfg, _ = log_cfg(
        str(log_file),
        log_level,
        logger_name=logger_name.replace("_", "."),
    )
    dictConfig(cfg)
    # Alter the Celery logger using the provided logger from kwargs if available.
    logger.setLevel(log_level)
    # Clear existing handlers and add the ones from the new configuration.
    logger.handlers.clear()
    configured_logger = logging.getLogger(logger_name.replace("_", "."))
    for handler in configured_logger.handlers:
        logger.addHandler(handler)


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
