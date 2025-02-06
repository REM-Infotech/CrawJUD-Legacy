"""Module: run.

This module serves as the entry point for the CrawJUD-Bots application, handling signal management and initializing the Flask app.
"""  # noqa: E501

from gevent import monkey

monkey.patch_all()
import logging  # noqa: E402
import signal  # noqa: E402
import subprocess  # nosec: B404 # noqa: S404, E402
import sys  # noqa: E402
import traceback  # noqa: E402
from os import getenv  # noqa: E402
from platform import system  # noqa: E402

from app import create_app  # noqa: E402

logger = logging.getLogger(__name__)


def handle_exit() -> None:
    """Handle graceful shutdown of the application.

    This function is triggered by termination signals to ensure the application exits cleanly.
    """
    sys.exit(0)


def start_vnc() -> None:
    """Start the TightVNC server for remote desktop access.

    Executes the TightVNC server with specified parameters and handles any exceptions that occur during startup.
    """
    try:
        # Executa o comando com verificação de erro
        subprocess.run(  # noqa: S603 # nosec: B607, B603
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
        logger.info("TightVNC iniciado com sucesso!")
    except Exception:
        err = traceback.format_exc()
        logger.exception(err)


if system().lower() == "linux" and getenv("INTO_DOCKER", None):
    start_vnc()

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

flask_app, __, app = create_app()
