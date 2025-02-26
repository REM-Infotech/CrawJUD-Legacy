"""Menu manager module."""

from contextlib import contextmanager
from typing import Any, Generator

import inquirer


class MenuManager:
    """Menu manager class."""

    thead_io = None
    current_choice = ""
    _current_menu: inquirer.List = None
    _current_menu_name = ""
    returns_message_ = []

    current_app = ""

    @contextmanager
    def answer_prompt(
        self,
        current_menu: inquirer.List,
        menu: dict[str, inquirer.List],
    ) -> Generator[
        dict[str, str],
        Any,
        None,
    ]:
        """Answer prompt context manager."""
        try:
            server_answer = inquirer.prompt([current_menu])
            choice = server_answer.get("application_list", "Back")

            latest_menu = self.current_menu_name

            if choice in menu:
                self.current_menu_name = choice
                self.current_menu = menu.get(choice)

            splited_currentmenuname = self.current_menu_name.split(" ")

            if len(splited_currentmenuname) > 2 and latest_menu == "Main Menu":
                self.current_app = f"{splited_currentmenuname[0]}_{splited_currentmenuname[1]}".lower()

            elif len(splited_currentmenuname) == 2:
                self.current_app = splited_currentmenuname[1].lower()

            if server_answer is None:
                server_answer = {"application_list": "Close Server"}
            yield server_answer
        finally:
            pass

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

    @property
    def main_menu(self) -> None:
        """Main menu for the server."""
        return inquirer.List(
            "application_list",
            message="Select application",
            choices=[
                "Start All",
                "Quart API ASGI",
                "Quart Web ASGI",
                "Celery Worker",
                "Celery Beat",
                "Get Bot LOG",
                "Clear Prompt",
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
    def worker_menu(self) -> inquirer.List:
        """Menu for Celery Worker."""
        self.current_choice = "Celery Worker"
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
    def beat_menu(self) -> inquirer.List:
        """Menu for Celery Beat."""
        self.current_choice = "Celery Beat"
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
