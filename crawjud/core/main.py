"""Server main entry point."""

from __future__ import annotations

from os import environ
from time import sleep

from termcolor import colored
from tqdm import tqdm

from crawjud import MasterApp
from crawjud.manager.menu import MenuManager
from crawjud.manager.runner import RunnerServices


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

    tqdm.write(colored("Server closed!", "green", attrs=["bold"]))
    sleep(2)


__all__ = [MenuManager, RunnerServices, main_server]
