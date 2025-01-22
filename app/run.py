import eventlet
eventlet.monkey_patch()

import signal
import subprocess
import sys
from os import getcwd, path
from pathlib import Path
from platform import system

# from clear import clear
from dotenv import dotenv_values as values

from app import create_app

def handle_exit() -> None:
    sys.exit(0)


def start_vnc() -> None:

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

if system().lower() == "linux":
    start_vnc()

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

app, io, celery = create_app()

