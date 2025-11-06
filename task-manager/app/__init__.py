"""CrawJUD - Sistema de Automação Jurídica."""

import importlib

from celery import Celery

import _hook as _
from config import config

__all__ = ["_"]


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Returns:
        Celery: Configured Celery instance.

    """
    app = Celery(__name__)
    dict_config = {
        k.lower(): v for k, v in list(config.as_dict().items())
    }
    app.config_from_object(dict_config)
    importlib.import_module("tasks", __package__)

    return app


app = make_celery()
