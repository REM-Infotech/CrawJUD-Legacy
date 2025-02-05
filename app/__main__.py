"""Main entry point for the CrawJUD-Bots application."""

import logging
import signal
import subprocess  # noqa: S404  # nosec: B404
import sys
from os import environ, getenv
from platform import system
from typing import Dict

from dotenv_vault import load_dotenv

from git_py import version_file

load_dotenv()

values = environ.get


def handle_exit() -> None:
    """Handle termination signals and exit the program gracefully."""
    sys.exit(0)


def start_vnc() -> None:
    """Start the TightVNC server with specified parameters.

    Raises:
        Exception: If the TightVNC server fails to start.

    """
    try:
        # Executa o comando com verificação de erro
        subprocess.run(  # noqa: S603, S607 # nosec: B607, B603
            [  # noqa: S607
                "tightvncserver",
                ":99",
                "-geometry",
                "1600x900",
                "-depth",
                "24",
                "-rfbport",
                "5999",
            ],
            check=True,  # Lança exceção se o comando falhar
        )
        logging.info("VNC Server started successfully.")
    except Exception:
        ...


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)


def start_app():
    """Initialize and start the Flask application with SocketIO.

    Sets up the application context, configures server settings,
    and starts the application using specified parameters.

    Raises:
        SystemExit: Exits the application on interruption.

    """
    from app import create_app

    app, io, _ = create_app()

    args_run: Dict[str, str | int | bool] = {}
    app.app_context().push()

    debug = values("DEBUG", "False").lower() in ("true")

    hostname = values("SERVER_HOSTNAME", "127.0.0.1") if getenv("INTO_DOCKER", None) else "127.0.0.1"

    unsafe_werkzeug = getenv("INTO_DOCKER", None) is None or (getenv("DEBUG", "False").lower() == "true")
    port = int(values("PORT", "8000"))
    version_file()
    if system().lower() == "linux":
        start_vnc()

    args_run = {"host": hostname, "debug": debug, "port": port, "allow_unsafe_werkzeug": unsafe_werkzeug}

    try:
        io.run(app, **args_run, log_output=True)
    except (KeyboardInterrupt, TypeError):
        if system().lower() == "linux":
            try:
                subprocess.run(["tightvncserver", "-kill", ":99"])  # noqa: S603, S607 # nosec: B603, B607

            except Exception:
                # err = traceback.format_exc()
                # app.logger.exception(err)
                ...

        sys.exit(0)


def dev_modules():
    """Verify that development dependencies are installed.

    Raises:
        ImportError: If any development dependencies are missing.

    """
    import importlib

    importlib.import_module("isort")
    importlib.import_module("black")
    importlib.import_module("ruff")
    importlib.import_module("mypy")
    # importlib.import_module("pytest")
    # importlib.import_module("pytest-cov")
    # importlib.import_module("pytest-mock")
    # importlib.import_module("yamllint")


if __name__ == "__main__":
    """
    Entry point for running the application.

    Loads environment variables, checks for debug mode,
    and starts the application.
    """
    if getenv("DEBUG", "False").lower() == "true":
        dev_modules()

    start_app()
