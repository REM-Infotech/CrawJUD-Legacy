"""Initialize the CrawJUD-Bots app with Quart, Celery, AsyncServer, and extension.

This module creates the Quart app and configures extensions like Celery,
AsyncServer, Quart-Mail, SQLAlchemy, and Talisman.
"""

import asyncio
import platform
import subprocess
import sys
from os import environ, getenv
from pathlib import Path
from threading import Thread

import quart_flask_patch  # noqa: F401
import uvicorn
from celery import Celery
from dotenv_vault import load_dotenv
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from quart import Quart as Quart
from socketio import ASGIApp

valides = [
    getenv("IN_PRODUCTION", None) is None,
    platform.system() == "Windows",
    getenv("DEBUG", "False").lower() == "true",
]

asc = any(valides)

load_dotenv()


mail = Mail()
tslm = Talisman()
db = SQLAlchemy()
app = Quart(__name__)


load_dotenv()

values = environ.get
is_init = Path("is_init.txt").resolve()


class AppFactory:
    """Factory to create and configure the ASGIApp and Celery."""

    async def main(self) -> tuple[Quart, ASGIApp, Celery]:
        """Run the main application loop."""
        task = asyncio.create_task(self.create_app())
        await task

        return task.result()

    async def create_app(self) -> tuple[Quart, ASGIApp, Celery]:
        """Create and configure the ASGIApp and Celery worker.

        Returns:
            tuple: A tuple containing ASGIApp and Celery worker.

        """
        from app.core.configurator import app_configurator

        return await app_configurator(app)

    @classmethod
    def construct_app(cls) -> tuple[Quart, Celery]:  # pragma: no cover
        """Initialize and start the Quart application with AsyncServer.

        Sets up the application context, configures server settings,
        and starts the application using specified parameters.

        Returns:
            tuple: A tuple containing the Quart application and Celery worker.

        """
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()

        quart, app, celery = loop.run_until_complete(AppFactory().main())
        args_run: dict[str, str | int | bool] = {}
        # app.app_context().push()

        debug = values("DEBUG", "False").lower() == "True"

        port = int(values("PORT", "8000"))

        args_run = {
            "debug": debug,
            "port": port,
            "log_output": True,
            "app": app,
        }

        try:
            application = getenv("APPLICATION_APP")
            in_production = getenv("IN_PRODUCTION", "False")

            if application != "beat":
                if application == "quart" and in_production == "True":
                    cls.starter(**args_run)

                elif application == "worker" and in_production == "False":
                    starter = Thread(target=cls.starter, kwargs=args_run)
                    starter.daemon = True
                    starter.start()

        except (KeyboardInterrupt, TypeError):
            sys.exit(0)

        return quart, celery

    @classmethod
    def starter(
        cls,
        port: int,
        log_output: bool,
        app: Quart,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Start the application with the specified parameters.

        Args:
            port (int): The port to listen on.
            log_output (bool): Whether to log output.
            app (Quart): The Quart application instance.
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        # Create a WebSocket

        port = kwargs.pop("port", port)
        log_output = kwargs.pop("log_output", log_output)
        app = kwargs.pop("app", app)

        hostname = getenv(
            "SERVER_HOSTNAME",
            subprocess.run(
                [
                    "powershell",
                    "hostname",
                ],
                capture_output=True,
                text=True,
            ).stdout.strip(),
        )

        uvicorn.run(
            app,
            host=hostname,
            port=port,
        )

    @staticmethod
    def handle_exit(a: any = None, b: any = None) -> None:
        """Handle termination signals and exit the program gracefully."""
        sys.exit(0)
