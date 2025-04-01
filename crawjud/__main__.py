"""Worker CrawJUD Manager."""

import asyncio
from os import getenv
from pathlib import Path
from threading import Event
from time import sleep
from typing import Callable, Dict

import inquirer
from clear import clear
from termcolor import colored
from tqdm import tqdm

from api import create_app
from api.config import running_servers
from crawjud.manager import HeadCrawjudManager

objects_config = {
    "development": "api.config.DevelopmentConfig",
    "production": "api.config.ProductionConfig",
    "testing": "api.config.TestingConfig",
}


class WorkerCrawJUD(HeadCrawjudManager):
    """Worker CrawJUD Manager."""

    loop_app = True

    def boot_app(self) -> None:
        """Boot Beat and the application."""
        clear()
        self.event_stop = Event()
        env_ambient = getenv("AMBIENT_CONFIG")
        ambient = objects_config[env_ambient]

        self.app = asyncio.run(create_app(ambient))

    def __init__(self, **kwargs: str) -> None:
        """Initialize the ASGI server."""
        self.boot_app()

        self.current_menu = self.main_menu
        self.current_menu_name = "Main Menu"

        if kwargs:
            self.start_specific(**kwargs)

    @property
    def functions(
        self,
    ) -> dict[
        str,
        Callable[[], None],
    ]:
        """Return the functions for the server."""
        return {
            "status": self.status,
            "start": self.start,
            "stop": self.stop,
            "restart": self.restart,
        }

    def prompt(self) -> None:
        """Prompt the user for server options."""
        if self.current_menu_name == "Main Menu":
            if running_servers:
                tqdm.write("=============================================================")
                tqdm.write("Running servers:")
                for server in running_servers.keys():
                    tqdm.write(f" {colored('[ x ]', color='green')} {server}")
                tqdm.write("=============================================================")

        if self.returns_message:
            message = self.returns_message[0]
            type_message = self.returns_message[1].upper()
            colour = self.returns_message[2]
            tqdm.write(colored(f"[{type_message}] {message}", colour, attrs=["blink", "bold"]))
            sleep(5)
            self.returns_message_ = ""
            clear()

        menu = {
            "Quart Application": self.quart_application,
            "Celery Worker": self.worker_menu,
            "Celery Beat": self.beat_menu,
        }

        translated_args: dict[str, str] = {
            "Start Service": "start",
            "Restart Service": "restart",
            "Shutdown Service": "stop",
            "View Logs": "status",
        }

        options: dict[str, Callable[[], None]] = {
            "Clear Prompt": clear,
            "Start Services": self.start_all,
            "Get Executions Logs": self.get_log_bot,
            "Close Server": self.close_server,
            "Back": self.return_main_menu,
        }
        with self.answer_prompt(self.current_menu, menu) as server_answer:
            func = None
            choice = server_answer.get("server_options", "Back")
            translated_arg = translated_args.get(choice)
            if translated_arg:
                func = self.functions.get(translated_arg)

            if choice == "Show Prompt":
                clear()

            elif choice in options:
                call_obj = options.get(choice)
                call_obj()

            elif func:
                returns = func(self.current_app)

                if returns is not None and returns != "":
                    self.returns_message_ = returns

            choice = self.current_choice
            if self.loop_app:
                self.prompt()

    def close_server(self) -> bool:
        """Close the server."""
        config_exit = inquirer.prompt([inquirer.Confirm("exit", message="Do you want to exit?")])
        if config_exit.get("exit") is True:
            clear()
            self.loop_app = False

            running_servers_ = running_servers.items()
            running_servers_ = [running_servers_ for running_servers_ in running_servers_]  # noqa: C416
            running_servers_ = running_servers_[::-1]
            for application_name, application in running_servers_:
                if application_name == "Quart":
                    self.event_stop.set()

                sleep(1)
                application.stop()
                sleep(1)

        self.return_main_menu()

    def get_log_bot(self) -> None:
        """Get the bot logs."""
        answer_logger: Dict[str, str | None] | None = inquirer.prompt([
            inquirer.Text("log", message="Enter the log file name")
        ])

        text_choice = answer_logger.get("log")

        if not text_choice:
            return

        file_path = (
            Path(__file__)
            .cwd()
            .resolve()
            .joinpath(
                "crawjud",
                "bot",
                "temp",
                text_choice,
                f"{text_choice}.log",
            )
        )
        tqdm.write(file_path.as_uri())
        if file_path.exists():
            from crawjud.utils.watch import monitor_log

            monitor_log(file_path=file_path)
            tqdm.write(colored("[INFO] Log file closed.", "yellow", attrs=["bold"]))
            sleep(2)
            clear()
            return

        tqdm.write(colored(f"[ERROR] File '{text_choice}' does not exist.", "red", attrs=["bold"]))
        sleep(2)
        clear()

    def return_main_menu(self) -> None:
        """Return to the main menu."""
        self.current_menu = self.main_menu
        self.current_menu_name = "Main Menu"
        self.current_choice = ""
        self.current_app = ""


instance = WorkerCrawJUD()

if getenv("SERVER_DEPLOYED", "False").lower() == "true":
    instance.start_quart()
else:
    instance.prompt()
