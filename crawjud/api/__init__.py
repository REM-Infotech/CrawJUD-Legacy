"""Quart application package."""

from __future__ import annotations

import asyncio
import logging
import re
from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

import quart_flask_patch as quart_patch
from clear import clear
from dotenv import dotenv_values
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
from quart_socketio import SocketIO
from termcolor import colored
from tqdm import tqdm

from crawjud.app_celery import make_celery
from crawjud.resources import check_cors_allowed_origins, workdir
from crawjud.utils.logger import dict_config
from crawjud.utils.middleware import ProxyHeadersMiddleware

if TYPE_CHECKING:
    from crawjud.interfaces import HealtCheck
    from crawjud.interfaces.types import ConfigName


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

config_name = environ.get("FLASK_ENV", "default")


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
    async with app.app_context():
        db.init_app(app)
        jwt.init_app(app)
        sess.init_app(app)
        mail.init_app(app)
        app.extensions["celery"] = make_celery()


@app.cli.command()
def init_database() -> None:
    """Inicializa o banco de dados criando todas as tabelas necessárias."""
    from crawjud.models import init_database

    asyncio.run(init_database())

    tqdm.write(
        colored(
            "Banco de dados inicializado com sucesso!",
            color="green",
            attrs=["bold", "blink"],
        ),
    )


async def main_app() -> None:
    """Asynchronously initializes and runs the main application.

    This function performs the following steps:
    1. Creates the application instance using `create_app()`.
    2. Initializes the I/O subsystem with the created app.
    3. Retrieves the host and port from environment variables,
        defaulting to "127.0.0.1" and 5000 if not set.
    4. Runs the application using the I/O subsystem on the specified host and port.

    """
    with suppress(KeyboardInterrupt):
        async with app.app_context():
            await io.init_app(
                app,
                cors_allowed_origins=check_cors_allowed_origins,
            )
            from crawjud.api.namespaces import register_namespaces

            await register_namespaces(io)
            # Use "127.0.0.1" como padrão para evitar exposição a todas as interfaces
            host = environ.get("API_HOST", "127.0.0.1")
            port = int(environ.get("API_PORT", 5000))

            log_folder = Path(__file__).cwd().joinpath("temp", "logs")
            log_folder.mkdir(exist_ok=True, parents=True)
            log_file = str(log_folder.joinpath(f"{__package__}.log"))
            cfg, _ = dict_config(
                LOG_LEVEL=logging.INFO,
                LOGGER_NAME=__package__,
                FILELOG_PATH=log_file,
            )

            # Executa o servidor sem SSL para evitar erros de requisição HTTP inválida
            await io.run(
                app,
                host=host,
                port=port,
                log_config=cfg,
                log_level=logging.INFO,
                ssl_keyfile=None,
                ssl_certfile=None,
            )


@app.route("/api/health")
def health_check() -> HealtCheck:
    """Verifique status de saúde da aplicação.

    Returns:
        HealtCheck: HealtCheck

    """
    try:
        # Testa conexão com banco de dados
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "erro"

    return {
        "status": "ok" if db_status == "ok" else "erro",
        "database": db_status,
        "timestamp": str(db.func.now()),
    }


@app.cli.command()
def start() -> None:
    """Executa o App."""
    try:
        clear()
        asyncio.run(main_app())
    except KeyboardInterrupt:
        from blessed import Terminal

        term = Terminal()

        tqdm.write(term.home + term.clear + term.move_y(term.height // 2))
        tqdm.write(
            term.black_on_darkkhaki(term.center("press any key to continue.")),
        )

        with term.cbreak(), term.hidden_cursor():
            term.inkey()

        clear()


__all__ = ["quart_patch"]
