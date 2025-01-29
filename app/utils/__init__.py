import re
from typing import Any

from celery import Celery
from os import environ
from dotenv_vault import load_dotenv
from flask import Flask

from .bots_logs import initialize_logging
from .get_location import GeoLoc

load_dotenv()


def make_celery(app: Flask) -> Celery:
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs) -> Any:  # -> Any:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def check_allowed_origin(origin="https://google.com") -> bool:  # pragma: no cover
    allowed_origins = [
        r"https:\/\/.*\.nicholas\.dev\.br",
        r"https:\/\/.*\.robotz\.dev",
        r"https:\/\/.*\.rhsolutions\.info",
        r"https:\/\/.*\.rhsolut\.com\.br",
    ]
    if not origin:
        origin = f'https://{environ.get("HOSTNAME")}'

    for orig in allowed_origins:
        pattern = orig
        matchs = re.match(pattern, origin)
        if matchs:
            return True

    return False


__all__ = ["make_celery", "check_allowed_origin", "initialize_logging", "GeoLoc"]
