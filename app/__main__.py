import signal
import subprocess
import sys

# import traceback
from os import environ, getenv
from platform import system
from typing import Dict

# from clear import clear
from dotenv_vault import load_dotenv

from git_py import version_file

load_dotenv()

values = environ.get


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
    except Exception:
        # err = traceback.format_exc()
        # app.logger.exception(err)
        ...


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)


if __name__ == "__main__":
    from app import create_app

    app, io, _ = create_app()

    args_run: Dict[str, str | int | bool] = {}
    app.app_context().push()

    debug = values("DEBUG", "False").lower() in ("true")

    hostname = (
        values("SERVER_HOSTNAME", "127.0.0.1")
        if getenv("DOCKER_CONTEXT", None)
        else "127.0.0.1"
    )

    unsafe_werkzeug = getenv("DOCKER_CONTEXT", None) is None or (
        getenv("DEBUG", "False").lower() == "true"
    )
    port = int(values("PORT", "8000"))
    version_file()
    if system().lower() == "linux":
        start_vnc()

    args_run = {
        "host": hostname,
        "port": port,
        "log_output": True,
        "allow_unsafe_werkzeug": unsafe_werkzeug,
    }

    try:
        io.run(app, **args_run)
    except (KeyboardInterrupt, TypeError):

        if system().lower() == "linux":

            try:
                subprocess.run(["tightvncserver", "-kill", ":99"])

            except Exception:
                # err = traceback.format_exc()
                # app.logger.exception(err)
                ...

        sys.exit(0)
