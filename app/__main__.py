import eventlet

eventlet.monkey_patch(socket=True)

import signal
import subprocess  # pragma: no cover
import sys
from os import getcwd, path  # pragma: no cover
from pathlib import Path
from platform import system

# from clear import clear  # pragma: no cover
from dotenv import dotenv_values as values  # pragma: no cover

from app import create_app  # pragma: no cover

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


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

app, io, celery = create_app()  # pragma: no cover

if __name__ == "__main__":  # pragma: no cover

    app.app_context().push()

    debug = values().get("DEBUG", "False").lower() in ("true")
    hostname = values().get("SERVER_HOSTNAME", "127.0.0.1")

    if system().lower() == "linux":
        start_vnc()

    version_file()

    reload_app = io.run(
        app, host=hostname, port=int(values().get("PORT", "8000")), log_output=True
    )
