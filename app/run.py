"""
Module: run.

This module serves as the entry point for the CrawJUD-Bots application, handling signal management and initializing the Flask app.
"""

import signal
import subprocess
import sys
from os import getenv
from platform import system

from app import create_app


def handle_exit() -> None:
    """
    Handle graceful shutdown of the application.

    This function is triggered by termination signals to ensure the application exits cleanly.
    """
    sys.exit(0)


def start_vnc() -> None:
    """
    Start the TightVNC server for remote desktop access.

    Executes the TightVNC server with specified parameters and handles any exceptions that occur during startup.
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
    except Exception as e:
        print(e)


if system().lower() == "linux" and getenv("INTO_DOCKER", None):
    start_vnc()

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

flask_app, __, app = create_app()
