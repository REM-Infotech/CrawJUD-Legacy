"""Main module for CrawJUD-Bots application."""

import signal
import subprocess
import sys
from os import environ, getenv
from platform import system
from typing import Dict

from dotenv_vault import load_dotenv

from git_py import version_file

load_dotenv()

values = environ.get


def handle_exit() -> None:
    """Handle the termination signal and exits the program."""
    sys.exit(0)


def start_vnc() -> None:
    """
    Start the TightVNC server with specified parameters.

    Raises:
        Exception: If the TightVNC server fails to start.
    """
    try:
        # Executa o comando com verificação de erro
        subprocess.run(
            [
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
        print("TightVNC iniciado com sucesso!")
    except Exception:
        ...


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)


def start_app():
    """
    Initialize and start the application.

    This function sets up the application context, configures the server
    settings, and starts the application using the specified parameters.
    It also handles cleanup operations when the application is interrupted.
    Raises:
        SystemExit: Exits the application when a KeyboardInterrupt or TypeError occurs.
    """
    from app import create_app

    app, io, _ = create_app()

    args_run: Dict[str, str | int | bool] = {}
    app.app_context().push()

    debug = values("DEBUG", "False").lower() in ("true")

    hostname = (
        values("SERVER_HOSTNAME", "127.0.0.1")
        if getenv("INTO_DOCKER", None)
        else "127.0.0.1"
    )

    unsafe_werkzeug = getenv("INTO_DOCKER", None) is None or (
        getenv("DEBUG", "False").lower() == "true"
    )
    port = int(values("PORT", "8000"))
    version_file()
    if system().lower() == "linux":
        start_vnc()

    args_run = {
        "host": hostname,
        "debug": debug,
        "port": port,
        "allow_unsafe_werkzeug": unsafe_werkzeug,
    }

    try:
        io.run(app, **args_run, log_output=True)
    except (KeyboardInterrupt, TypeError):
        if system().lower() == "linux":
            try:
                subprocess.run(["tightvncserver", "-kill", ":99"])

            except Exception:
                # err = traceback.format_exc()
                # app.logger.exception(err)
                ...

        sys.exit(0)


def dev_modules():
    """
    Check dev dependencies are installed.

    Raises:
        ImportError: If any of the dev dependencies are not installed.
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
    if getenv("DEBUG", "False").lower() == "true":
        dev_modules()

    start_app()
