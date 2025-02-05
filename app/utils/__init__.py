"""Utility functions and classes for the CrawJUD-Bots application."""

import re
from os import environ

from celery import Celery
from dotenv_vault import load_dotenv
from flask import Flask

from .bots_logs import init_log
from .get_location import GeoLoc

load_dotenv()


def make_celery(app: Flask) -> Celery:
    """Create and configure a Celery instance with Flask application context.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY"])

    class ContextTask(celery.Task):
        def __call__(self, *args: tuple, **kwargs: dict) -> any:  # -> any:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def check_allowed_origin(origin: str = "https://google.com") -> bool:
    """Check if the origin is allowed based on predefined patterns.

    Args:
        origin (str, optional): The origin to check. Defaults to "https://google.com".

    Returns:
        bool: True if origin is allowed, False otherwise.

    """
    allowed_origins = [
        r"https:\/\/.*\.nicholas\.dev\.br",
        r"https:\/\/.*\.robotz\.dev",
        r"https:\/\/.*\.rhsolutions\.info",
        r"https:\/\/.*\.rhsolut\.com\.br",
    ]
    if not origin:
        origin = f"https://{environ.get('HOSTNAME')}"

    for orig in allowed_origins:
        pattern = orig
        matchs = re.match(pattern, origin)
        if matchs:
            return True

    return False


__all__ = ["GeoLoc", "check_allowed_origin", "init_log", "make_celery"]
