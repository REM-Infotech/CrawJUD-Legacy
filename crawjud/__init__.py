"""Main module for the CrawJUD Package."""

import asyncio
from pathlib import Path
from time import sleep

import inquirer
from billiard.context import Process
from celery.apps.beat import Beat
from clear import clear
from socketio import AsyncServer
from termcolor import colored
from tqdm import tqdm

from crawjud.config import running_servers
from crawjud.core import create_app
from crawjud.menu_manager import MenuManager

io = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=10,
)
clear()


def start_beat() -> None:
    """Start the Celery beat scheduler."""
    from crawjud.core import create_app

    async def beat_start() -> None:
        async with app.app_context():
            beat = Beat(
                app=celery,
                scheduler="crawjud.utils.scheduler:DatabaseScheduler",
                quiet=True,
            )
            beat.run()

    app, _, _, celery = asyncio.run(create_app())
    asyncio.run(beat_start())


class MasterApp(MenuManager):
    """Master application class."""

    def __init__(self) -> None:
        """Initialize the ASGI server."""
        self.current_menu = self.main_menu
        self.app, self.srv, self.asgi, self.celery = asyncio.run(create_app())
        Process(target=start_beat, daemon=True).start()
        clear()

    def prompt(self) -> None:
        """Prompt the user for server options."""
        self.current_menu_name = "Main Menu"
        while True:
            clear()

            if self.current_menu_name == "Main Menu":
                if running_servers:
                    tqdm.write("=============================================================")
                    tqdm.write("Running servers:")
                    for server in running_servers.keys():
                        tqdm.write(f" - {server}")
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

            with self.answer_prompt(self.current_menu, menu) as server_answer:
                choice = server_answer.get("application_list", "Back")

                if choice == "Clear Prompt":
                    clear()
                    continue

                if choice == "Start All":
                    for _, functions in self.functions.items():
                        func = functions.get("Start Server")
                        asyncio.run(func())

                    tqdm.write(colored("[INFO] All servers started.", "green", attrs=["bold"]))
                    sleep(2)
                    continue

                if choice == "Get Bot LOG":
                    self.get_log_bot()
                    tqdm.write(colored("[INFO] Log file closed.", "yellow", attrs=["bold"]))
                    sleep(2)
                    continue

                if choice == "Close Server":
                    config_exit = inquirer.prompt([inquirer.Confirm("exit", message="Do you want to exit?")])
                    if config_exit.get("exit") is True:
                        self.application.join()
                        clear()
                        tqdm.write("Server closed.")
                        break

                    self.return_main_menu()
                    continue

                elif choice == "Back":
                    self.return_main_menu()
                    continue

                func = self.functions.get(self.current_app).get(choice)
                if func:
                    returns = func()

                    if returns is not None and returns != "":
                        self.returns_message_ = returns

                choice = self.current_choice

    def return_main_menu(self) -> None:
        """Return to the main menu."""
        self.current_menu = self.main_menu
        self.current_menu_name = "Main Menu"
        self.current_choice = ""
        self.current_app = ""

    def get_log_bot(self) -> None:
        """Get the bot logs."""
        answer_logger = inquirer.prompt([inquirer.Text("log", message="Enter the log file name")])

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
            from crawjud.core.watch import monitor_log

            monitor_log(file_path=file_path)
            return

        tqdm.write(colored(f"[ERROR] File '{text_choice}' does not exist.", "red", attrs=["bold"]))
        sleep(2)
        clear()
