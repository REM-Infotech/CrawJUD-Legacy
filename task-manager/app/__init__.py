"""CrawJUD - Sistema de Automação Jurídica."""

import importlib

from celery import Celery

from config import settings

app = Celery(__name__)


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    importlib.import_module("app.tasks", __package__)
    app.config_from_object(settings)
    return app


make_celery()
