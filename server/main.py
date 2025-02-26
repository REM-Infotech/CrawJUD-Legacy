"""Server main entry point."""

from os import environ

from tqdm import tqdm

from server import MasterApp


def main_server() -> None:
    """Server main entry point."""
    application_instance = MasterApp()

    environ.update({
        "SERVER_MANAGEMENT": "True",
    })
    try:
        application_instance.prompt()

    except KeyboardInterrupt:
        tqdm.write("Stopping app")
        application_instance.thead_io.join(10)
