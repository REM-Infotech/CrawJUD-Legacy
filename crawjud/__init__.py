"""CrawJUD Robots Process Automation Application."""

import warnings
from os import environ
from pathlib import Path

import quart_flask_patch  # noqa: F401
from celery import Celery

from api import app
from crawjud.utils import make_celery

warnings.filterwarnings("ignore", category=RuntimeWarning, module="google_crc32c")


values = environ.get
is_init = Path("is_init.txt").resolve()


async def create_celery_app() -> Celery:
    """Load configuration settings into the Quart application.

    Args:
        app: The Quart application instance to configure

    Returns:
        None

    """
    async with app.app_context():
        celery = None
        celery = await make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery
        celery.autodiscover_tasks(["crawjud.bot", "crawjud.utils"])

    return celery
