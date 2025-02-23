"""ASGI server module."""

# import sys

import asyncio
from importlib import import_module

import inquirer
from clear import clear
from socketio import ASGIApp, AsyncServer
from tqdm import tqdm  # noqa: F401

import server.celery_beat
import server.celery_worker
import server.quart
from server.thead_asgi import ASGIServer

io = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=10,
)

import_module("server.logs", __package__)

clear()


class MasterApp:
    """Master application class."""

    thead_io = None
    current_choice = ""
    _current_menu: inquirer.List = None
    returns_message_ = ""
    functions = {
        "quart": {
            "Start Server": server.quart.start,
            "Close Server": server.quart.shutdown,
            "View Logs": server.quart.status,
        },
        "worker": {
            "Start Worker": server.celery_worker.start,
            "Close Worker": server.celery_worker.shutdown,
            "View Logs": server.celery_worker.status,
        },
        "beat": {
            "Start Beat": server.celery_beat.start,
            "Close Beat": server.celery_beat.shutdown,
            "View Logs": server.celery_beat.status,
        },
    }

    @property
    def current_menu(self) -> None:
        """Return the current menu."""
        return self._current_menu

    @current_menu.setter
    def current_menu(self, value: inquirer.List) -> None:
        """Set the current menu."""
        self._current_menu = value

    def __init__(self) -> None:
        """Initialize the ASGI server."""
        self.asgi_app = ASGIApp(io)
        self.application = ASGIServer.startio_srv(self.asgi_app)
        self.current_menu = self.main_menu

    @property
    def main_menu(self) -> None:
        """Main menu for the server."""
        return inquirer.List(
            "application_list",
            message="Select application",
            choices=["Quart ASGI", "Celery Worker", "Celery Beat", "Close Server"],
        )

    @property
    def quart_menu(self) -> inquirer.List:
        """Menu for Quart ASGI."""
        self.current_app = "quart"
        self.current_choice = "Quart ASGI"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=["Start Server", "Close Server", "View Logs", "Back"],
        )

    @property
    def worker_menu(self) -> inquirer.List:
        """Menu for Celery Worker."""
        self.current_app = "worker"
        self.current_choice = "Celery Worker"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=["Start Worker", "Close Worker", "View Logs", "Back"],
        )

    @property
    def beat_menu(self) -> inquirer.List:
        """Menu for Celery Beat."""
        self.current_app = "beat"
        self.current_choice = "Celery Beat"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=["Start Beat", "Close Beat", "View Logs", "Back"],
        )

    def prompt(self) -> None:
        """Prompt the user for server options."""
        while True:
            clear()

            if self.returns_message_ != "":
                tqdm.write(self.returns_message_)
                self.returns_message_ = ""

            menu = {
                "Quart ASGI": self.quart_menu,
                "Celery Worker": self.worker_menu,
                "Celery Beat": self.beat_menu,
            }

            server_answer = inquirer.prompt([self.current_menu])

            if server_answer is None:
                server_answer = {"application_list": "Close Server"}

            choice = server_answer.get("application_list", "Back")
            if choice == "Close Server":
                clear()
                config_exit = inquirer.prompt([inquirer.Confirm("exit", message="Do you want to exit?")])
                if config_exit.get("exit") is True:
                    self.application.join()
                    clear()
                    tqdm.write("Server closed.")
                    break

                self.current_menu = self.main_menu
                continue

            if choice == "Back":
                self.current_menu = self.main_menu
                continue

            elif choice != "Close Server" and choice != "Back":
                func = self.functions.get(self.current_app).get(choice)
                if func:
                    returns = asyncio.run(func())

                    if returns is not None and returns != "":
                        self.returns_message_ = returns
                    choice = self.current_choice
            self.current_menu = menu.get(choice)
