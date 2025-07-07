"""Initialize the CrawJUD-Bots app with Quart, Celery, AsyncServer, and extension.

This module creates the Quart app and configures extensions like Celery,
AsyncServer, Quart-Mail, SQLAlchemy, and Talisman.
"""

import warnings
from os import environ, getenv
from pathlib import Path

import quart_flask_patch  # noqa: F401
from celery import Celery
from dotenv import load_dotenv
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from quart import Quart as Quart
from redis import Redis
from socketio import ASGIApp

from crawjud.custom import QuartLoginManager as LoginManager

warnings.filterwarnings("ignore", category=RuntimeWarning, module="google_crc32c")

load_dotenv()

db = SQLAlchemy()
tlsm = Talisman()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar essa página."
login_manager.login_message_category = "info"


template_path = str(Path(__file__).parent.resolve().joinpath("templates"))
src_path = str(Path(__file__).parent.resolve().joinpath("static"))
app = Quart(__name__, static_folder=src_path, template_folder=template_path)

app.config.update({
    "SESSION_TYPE": "redis",
    "SESSION_REDIS": Redis(
        host=getenv("REDIS_HOST"),
        port=6379,
        db=2,
    ),
})

Session(app)
load_dotenv()

values = environ.get
is_init = Path("is_init.txt").resolve()


async def create_app() -> tuple[Quart, ASGIApp, Celery]:
    """Create and configure the ASGIApp and Celery worker.

    Returns:
        tuple: A tuple containing ASGIApp and Celery worker.

    """
    from crawjud.core.configurator import app_configurator

    return await app_configurator(app)
