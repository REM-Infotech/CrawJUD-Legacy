"""Quart application package."""

from __future__ import annotations  # noqa: I001


import quart_flask_patch as quart_patch
import logging
import re
from contextlib import suppress
from importlib import import_module
from typing import TYPE_CHECKING


from dotenv import dotenv_values
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
from quart_socketio import SocketIO
from crawjud.app_celery import make_celery
from crawjud.resources import check_cors_allowed_origins, workdir
from crawjud.utils.logger import dict_config
from crawjud.utils.middleware import ProxyHeadersMiddleware

if TYPE_CHECKING:
    from crawjud.interfaces.types import ConfigName


environ = dotenv_values()

jwt = JWTManager()
db = SQLAlchemy()
mail = Mail()

io = SocketIO(
    async_mode="asgi",
    launch_mode="uvicorn",
    cookie="access",
)

config_name = environ.get("FLASK_ENV", "default")
app = Quart(__name__)


async def create_app(config_name: ConfigName = "default") -> Quart:
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
    cors(
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
    return app


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
        from app.routes.auth import auth
        from app.routes.bot import bot
        from app.routes.config import admin
        from app.routes.credentials import cred
        from app.routes.execution import exe

        # Dynamically import additional route modules as needed.
        import_module("app.routes", package=__package__)

        list_blueprints = [bot, auth, exe, cred, admin]

        for bp in list_blueprints:
            app.register_blueprint(bp)


async def init_extensions(app: Quart) -> None:
    """Initialize and configure the application extensions.

    Args:
        app (Quart): The Quart application instance

    """
    async with app.app_context():
        db.init_app(app)
        jwt.init_app(app)
        mail.init_app(app)
        app.extensions["celery"] = make_celery()


async def main_app() -> Quart:
    """Asynchronously initializes and runs the main application.

    Returns:
        Quart: The initialized Quart application instance.

    """
    with suppress(KeyboardInterrupt):
        app = await create_app(config_name=config_name)
        async with app.app_context():
            # Obtém o diretório raiz do projeto de forma síncrona
            from pathlib import Path as SyncPath

            root_path = SyncPath(__file__).parent
            from app.namespaces import register_namespaces

            await io.init_app(
                app,
                cors_allowed_origins=check_cors_allowed_origins,
            )

            await register_namespaces(io)
            # Use "127.0.0.1" como padrão para evitar exposição a todas as interfaces
            host = environ.get("API_HOST", "127.0.0.1")
            port = int(environ.get("API_PORT", 5000))

            log_folder = root_path.joinpath("temp", "logs")
            log_folder.mkdir(exist_ok=True, parents=True)
            log_file = str(log_folder.joinpath(f"{__package__}.log"))
            cfg, _ = dict_config(
                LOG_LEVEL=logging.INFO,
                LOGGER_NAME=__package__,
                FILELOG_PATH=log_file,
            )

            # Executa o servidor sem SSL para evitar erros de requisição HTTP inválida
            return app


__all__ = ["quart_patch"]
