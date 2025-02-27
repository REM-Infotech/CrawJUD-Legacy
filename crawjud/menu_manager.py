"""Menu manager module."""

from contextlib import contextmanager
from platform import node
from threading import Event, Thread
from time import sleep
from typing import Any, Generator

import inquirer
from celery import Celery
from celery.apps.worker import Worker
from clear import clear
from quart import Quart
from socketio import ASGIApp
from tqdm import tqdm
from uvicorn import Server

from crawjud.config import StoreThread, running_servers
from crawjud.core.watch import monitor_log
from crawjud.utils import worker_name_generator


class MenuManager:
    """Menu manager class."""

    thead_io = None
    current_choice = ""
    _current_menu: inquirer.List = None
    _current_menu_name = ""
    returns_message_ = []
    current_app = ""

    celery_: Celery
    app_: Quart
    srv_: Server
    asgi_: ASGIApp

    @property
    def celery(self) -> Celery:
        """Return the celery instance."""
        return self.celery_

    @celery.setter
    def celery(self, value: Celery) -> None:
        """Set the celery instance."""
        self.celery_ = value

    @property
    def app(self) -> Quart:
        """Return the app instance."""
        return self.app_

    @app.setter
    def app(self, value: Quart) -> None:
        """Set the app instance."""
        self.app_ = value

    @property
    def srv(self) -> Server:
        """Return the server instance."""
        return self.srv_

    @srv.setter
    def srv(self, value: Server) -> None:
        """Set the server instance."""
        self.srv_ = value

    @property
    def asgi(self) -> ASGIApp:
        """Return the ASGI instance."""
        return self.asgi_

    @asgi.setter
    def asgi(self, value: ASGIApp) -> None:
        """Set the ASGI instance."""
        self.asgi_ = value

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
                "Quart Application",
                "Quart Web ASGI",
                "Celery Worker",
                "Celery Beat",
                "Get Bot LOG",
                "Clear Prompt",
                "Close Server",
            ],
        )

    @property
    def quart_application(self) -> inquirer.List:
        """Menu for Quart API."""
        self.current_choice = "Quart Application"
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

    def start_worker(self, stop_event: Event) -> None:
        """Run the Celery worker in a thread controlled by a stop event.

        Args:
            stop_event (Event): Event to signal the thread to stop.

        """
        worker_name = f"{worker_name_generator}@{node()}"
        worker = Worker(
            app=self.celery,
            hostname=worker_name,
            task_events=True,
            loglevel="INFO",
            concurrency=50.0,
            pool="threads",
        )
        Thread(target=worker.start, name="Worker Celery").start()
        while not stop_event.is_set():
            sleep(1)

        worker.stop()

    def start_quart(self, stop_event: Event) -> None:
        """Run the Quart server in a thread controlled by a stop event.

        Args:
            stop_event (Event): Event to signal the thread to stop.

        """
        while not stop_event.is_set():
            ...

    def start_all(self) -> None:
        """Start all server components in separate threads and allow stopping with an event.

        This method creates threads for the worker, Quart server, and Celery beat.
        It listens for a keyboard interrupt and then signals all threads to stop.
        """
        stop_event = Event()
        worker_thread = Thread(target=self.start_worker, args=(stop_event,))
        quart_thread = Thread(target=self.start_quart, args=(stop_event,))

        worker_thread.start()
        quart_thread.start()

        store_thread = StoreThread(
            process_name="Worker",
            process_id=worker_thread.ident,
            process_status="Running",
        )

        running_servers["Worker"] = store_thread

    def status(self) -> None:
        """Log the status of the server."""
        if not running_servers.get("Quart API"):
            return ["Server not running.", "ERROR", "red"]

        clear()
        tqdm.write("Type 'ESC' to exit.")

        monitor_log("uvicorn_api.log")

        return ["Exiting logs.", "INFO", "yellow"]
