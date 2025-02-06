"""Utility functions and classes for the CrawJUD-Bots application."""

import re  # noqa: E402
from os import environ  # noqa: E402

from celery import Celery  # noqa: E402
from dotenv_vault import load_dotenv  # noqa: E402
from flask import Flask  # noqa: E402

from .bots_logs import init_log  # noqa: E402
from .get_location import GeoLoc  # noqa: E402

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
