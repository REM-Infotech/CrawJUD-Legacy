"""Quart application package."""

from __future__ import annotations

import re
from importlib import import_module
from pathlib import Path

import quart_flask_patch as quart_patch
from dotenv import dotenv_values
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
from quart_socketio import SocketIO

from crawjud.app_celery import make_celery
from crawjud.utils.middleware import ProxyHeadersMiddleware


def check_cors_allowed_origins(*args, **kwargs) -> bool:
    return True


environ = dotenv_values()
sess = Session()
app = Quart(__name__)
jwt = JWTManager()
db = SQLAlchemy()
mail = Mail()

io = SocketIO(
    async_mode="asgi",
    launch_mode="uvicorn",
    cookie="access",
)

workdir = Path(__file__).cwd()


async def create_app(config_name: str = "default") -> Quart:
    """Create and configure the Quart application instance.

    Args:
        config_name (str): Nome da configuração a ser utilizada

    Returns:
        ASGIApp: The ASGI application instance with CORS and middleware applied.

    """
    file_config = workdir.joinpath("crawjud", "quartconf.py")
    app.config.from_pyfile(file_config)

    async with app.app_context():
        await init_extensions(app)
        await register_routes(app)

    app.asgi_app = ProxyHeadersMiddleware(app.asgi_app)
    return cors(
        app,
        allow_origin=[re.compile(r"^https?:\/\/[^\/]+")],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "x-xsrf-token",
            "X-Xsrf-Token",
        ],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_credentials=True,
    )


async def database_start(app: Quart) -> None:
    """Initialize and configure the application database.

    This function performs the following tasks:
    1. Checks if the current server exists in the database
    2. Creates a new server entry if it doesn't exist
    3. Initializes all database tables

    Args:
        app (Quart): The Quart application instance

    Note:
        This function requires the following environment variables:
        - NAMESERVER: The name of the server
        - HOSTNAME: The address of the server

    """


async def register_routes(app: Quart) -> None:
    """Register application's blueprints and error handlers with the Quart instance.

    This function manages the application's routing configuration by:
    1. Dynamically importing required route modules
    2. Registering blueprints for bot and webhook endpoints
    3. Setting up application-wide error handlers

    Args:
        app (Quart): The Quart application instance to configure

    Note:
        Currently registers 'bot' and 'webhook' blueprints, and imports
        logs routes automatically.

    """
    async with app.app_context():
        # Dynamically import additional route modules as needed.
        import_module("crawjud.api.routes", package=__package__)

    from crawjud.api.routes.auth import auth
    from crawjud.api.routes.bot import bot
    from crawjud.api.routes.config import admin
    from crawjud.api.routes.credentials import cred
    from crawjud.api.routes.dashboard import dash
    from crawjud.api.routes.execution import exe

    list_blueprints = [bot, auth, exe, dash, cred, admin]

    for bp in list_blueprints:
        app.register_blueprint(bp)


async def init_extensions(app: Quart) -> None:
    """Initialize and configure the application extensions.

    Args:
        app (Quart): The Quart application instance

    """
    db.init_app(app)
    jwt.init_app(app)
    sess.init_app(app)
    mail.init_app(app)
    app.extensions["celery"] = make_celery()

    async with app.app_context():
        await database_start(app)


__all__ = ["quart_patch"]
