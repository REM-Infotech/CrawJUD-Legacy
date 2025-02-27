"""Server main entry point."""

from __future__ import annotations

from os import environ

from tqdm import tqdm

from crawjud import MasterApp
from crawjud.crawjud_manager.menu import MenuManager
from crawjud.crawjud_manager.runner import RunnerServices


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

    tqdm.write("Server closed.")


__all__ = [MenuManager, RunnerServices, main_server]
