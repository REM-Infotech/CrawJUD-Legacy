"""Celery configuration for Quart application."""

import logging  # noqa: F401
from os import environ, getcwd, getenv  # noqa: F401
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

    logger.handlers.clear()

    worker_name = environ.get("WORKER_NAME")
    log_level = int(environ.get("LOG_LEVEL", 20))
    workdir_path = Path(__file__).cwd()
    log_file = workdir_path.joinpath("crawjud", "logs", f"{worker_name}.log")
    log_file.parent.mkdir(exist_ok=True, parents=True)

    cfg, _ = log_cfg(
        log_file=str(log_file),
        log_level=log_level,
        logger_name=worker_name,
    )

    dictConfig(cfg)
    handlers = logging.getLogger(worker_name).handlers
    for handler in handlers:
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
