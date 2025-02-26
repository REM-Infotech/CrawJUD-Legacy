"""Celery configuration for Quart application."""

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

    cfg, _ = log_cfg()
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
