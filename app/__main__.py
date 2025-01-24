import signal
import subprocess
import sys
from os import getcwd, path, getenv, environ
from pathlib import Path
from platform import system
import traceback

# from clear import clear
from dotenv import load_dotenv

from app import create_app

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
        err = traceback.format_exc()
        app.logger.exception(err)


def version_file() -> None:

    version_Path = Path(path.join(getcwd(), ".version"))
    if version_Path.exists() is False:
        from app.misc.checkout import checkout_release_tag

        with open(".version", "w") as f:
            f.write(checkout_release_tag())


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

app, io, _ = create_app()

if __name__ == "__main__":

    args_run = {}
    app.app_context().push()

    debug = values("DEBUG", "False").lower() in ("true")

    version_file()
    hostname = "127.0.0.1"
    if system().lower() == "linux":
        start_vnc()

        args_run = {
            "app": app,
            "host": hostname,
            "port": int(values("PORT", "8000")),
            "log_output": True,
            "allow_unsafe_werkzeug": True,
        }

        if getenv("DOCKER_CONTEXT", None):

            hostname = values("SERVER_HOSTNAME", "127.0.0.1")
            args_run = {
                "app": app,
                "host": hostname,
                "port": int(values("PORT", "8000")),
                "log_output": True,
            }

    elif system().lower() == "windows":
        args_run = {
            "app": app,
            "host": hostname,
            "port": int(values("PORT", "8000")),
            "log_output": True,
            "allow_unsafe_werkzeug": True,
        }

    reload_app = io.run(**args_run)
