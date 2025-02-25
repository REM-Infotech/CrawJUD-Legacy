"""ASGI server module."""

# import sys

import asyncio
from importlib import import_module
from time import sleep

import inquirer
from clear import clear
from socketio import ASGIApp, AsyncServer
from termcolor import colored
from tqdm import tqdm

import server.celery_beat
import server.celery_worker
import server.quart
import server.quart_web
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

    def prompt(self) -> None:
        """Prompt the user for server options."""
        self.current_menu_name = "Main Menu"
        while True:
            clear()

            if self.returns_message:
                message = self.returns_message[0]
                type_message = self.returns_message[1].upper()
                colour = self.returns_message[2]
                tqdm.write(colored(f"[{type_message}] {message}", colour, attrs=["blink", "bold"]))
                sleep(5)
                self.returns_message_ = ""
                clear()

            menu = {
                "Quart Web ASGI": self.quart_menu_web,
                "Quart API ASGI": self.quart_menu_api,
                "Celery Worker": self.worker_menu,
                "Celery Beat": self.beat_menu,
            }

            server_answer = inquirer.prompt([self.current_menu])

            if server_answer is None:
                server_answer = {"application_list": "Close Server"}

            choice = server_answer.get("application_list", "Back")

            close_app_context = all([
                choice == "Close Server",
                self.current_menu_name != "Main Menu",
            ])
            close_server_context = all([
                choice == "Close Server",
                self.current_menu_name == "Main Menu",
            ])

            if choice in menu:
                self.current_menu_name = choice
                self.current_menu = menu.get(choice)

            if close_app_context or choice != "Back" and self.current_menu_name != "Main Menu":
                splited_currentmenuname = self.current_menu_name.split(" ")
                self.current_app = splited_currentmenuname[0].lower()
                if len(splited_currentmenuname) > 2:
                    self.current_app = f"{splited_currentmenuname[0]}_{splited_currentmenuname[1]}".lower()
                func = self.functions.get(self.current_app).get(choice)
                if func:
                    returns = asyncio.run(func())

                    if returns is not None and returns != "":
                        self.returns_message_ = returns

                choice = self.current_choice

            elif close_server_context or choice == "Back":
                clear()

                if close_server_context:
                    config_exit = inquirer.prompt([inquirer.Confirm("exit", message="Do you want to exit?")])
                    if config_exit.get("exit") is True:
                        self.application.join()
                        clear()
                        tqdm.write("Server closed.")
                    break

                self.current_menu = self.main_menu
                self.current_app = ""
                self.current_choice = ""
                self.current_menu_name = "Main Menu"
                continue

    thead_io = None
    current_choice = ""
    _current_menu: inquirer.List = None
    _current_menu_name = ""
    returns_message_ = []

    current_app = ""

    functions = {
        "quart_api": {
            "Start Server": server.quart.start,
            "Shutdown App": server.quart.shutdown,
            "Restart App": server.quart.restart,
            "View Logs": server.quart.status,
        },
        "quart_web": {
            "Start Server": server.quart_web.start,
            "Shutdown App": server.quart_web.shutdown,
            "Restart App": server.quart_web.restart,
            "View Logs": server.quart_web.status,
        },
        "worker": {
            "Start Worker": server.celery_worker.start,
            "Shutdown App": server.celery_worker.shutdown,
            "Restart App": server.celery_worker.restart,
            "View Logs": server.celery_worker.status,
        },
        "beat": {
            "Start Beat": server.celery_beat.start,
            "Shutdown App": server.celery_beat.shutdown,
            "Restart App": server.celery_beat.restart,
            "View Logs": server.celery_beat.status,
        },
    }

    @property
    def returns_message(self) -> list[str]:
        """Return the returns message."""
        return self.returns_message_

    @returns_message.setter
    def returns_message(self, value: list[str]) -> None:
        """Set the returns message."""
        self.returns_message_ = value

    @property
    def current_menu_name(self) -> str:
        """Return the current menu name."""
        return self._current_menu_name

    @current_menu_name.setter
    def current_menu_name(self, value: str) -> None:
        """Set the current menu name."""
        self._current_menu_name = value

    @property
    def current_menu(self) -> str:
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
            choices=[
                "Quart API ASGI",
                "Quart Web ASGI",
                "Celery Worker",
                "Celery Beat",
                "Close Server",
            ],
        )

    @property
    def quart_menu_api(self) -> inquirer.List:
        """Menu for Quart API."""
        self.current_choice = "Quart API ASGI"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=[
                "Start Server",
                "Restart App",
                "Shutdown App",
                "View Logs",
                "Back",
            ],
        )

    @property
    def quart_menu_web(self) -> inquirer.List:
        """Menu for Quart Web ASGI."""
        self.current_choice = "Quart Web ASGI"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=[
                "Start Server",
                "Restart App",
                "Shutdown App",
                "View Logs",
                "Back",
            ],
        )

    @property
    def worker_menu(self) -> inquirer.List:
        """Menu for Celery Worker."""
        self.current_choice = "Celery Worker"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=[
                "Start Worker",
                "Restart App",
                "Shutdown App",
                "View Logs",
                "Back",
            ],
        )

    @property
    def beat_menu(self) -> inquirer.List:
        """Menu for Celery Beat."""
        self.current_choice = "Celery Beat"
        return inquirer.List(
            "application_list",
            message="Select an option",
            choices=[
                "Start Beat",
                "Restart App",
                "Shutdown App",
                "View Logs",
                "Back",
            ],
        )
