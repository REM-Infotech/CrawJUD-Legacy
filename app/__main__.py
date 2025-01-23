import signal
import subprocess
import sys
from os import getcwd, path, getenv
from pathlib import Path
from platform import system

# from clear import clear
from dotenv import dotenv_values as values

from app import create_app

# clear()


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
    except subprocess.CalledProcessError as e:

        print(f"Erro ao iniciar o TightVNC: {e}")
        raise e


def version_file() -> None:

    version_Path = Path(path.join(getcwd(), ".version"))
    if version_Path.exists() is False:
        from app.misc.checkout import checkout_release_tag

        with open(".version", "w") as f:
            f.write(checkout_release_tag())


if system().lower() == "linux" and getenv("DOCKER_CONTEXT", None):
    start_vnc()

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

app, io, _ = create_app()

if __name__ == "__main__":

    app.app_context().push()

    debug = values().get("DEBUG", "False").lower() in ("true")
    hostname = values().get("SERVER_HOSTNAME", "127.0.0.1")

    version_file()

    reload_app = io.run(
        app, host=hostname, port=int(values().get("PORT", "8000")), log_output=True
    )
