"""ASGI server module."""

# import sys

import inquirer
from clear import clear
from socketio import ASGIApp, AsyncServer
from tqdm import tqdm  # noqa: F401

from server.thead_asgi import ASGIServer

io = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=10,
)

clear()


class MasterApp:
    """Master application class."""

    thead_io = None

    _current_menu: inquirer.List = None

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
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=["Start Server", "Close Server", "View Logs", "Back"],
        )

    @property
    def worker_menu(self) -> inquirer.List:
        """Menu for Celery Worker."""
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=["Start Worker", "Close Worker", "View Logs", "Back"],
        )

    @property
    def beat_menu(self) -> inquirer.List:
        """Menu for Celery Beat."""
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=["Start Beat", "Close Beat", "View Logs", "Back"],
        )

    def prompt(self) -> None:
        """Prompt the user for server options."""
        while True:
            clear()
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

            self.current_menu = menu.get(choice)
