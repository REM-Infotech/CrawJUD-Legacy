"""Execute a aplicação Flask LexGestão API."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import suppress
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from clear import clear
from termcolor import colored
from tqdm import tqdm

from crawjud.api import check_cors_allowed_origins, create_app, db, io
from crawjud.utils.logger import dict_config

if TYPE_CHECKING:
    from crawjud.interfaces import HealtCheck

# Cria instância da aplicação baseada na configuração do ambiente
config_name = os.environ.get("FLASK_ENV", "default")
app = asyncio.run(create_app(config_name))


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
