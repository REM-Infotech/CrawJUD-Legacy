"""CrawJUD - Sistema de Automação Jurídica."""

import importlib

import resources._hook as _
from celery import Celery

from config import settings

__all__ = ["_"]


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    app = Celery(__name__)
    dict_config = {k.lower(): v for k, v in list(settings.as_dict().items())}
    app.config_from_object(dict_config)
    importlib.import_module("tasks", __package__)

    return app


app = make_celery()
