"""Main module for the CrawJUD Package."""

import asyncio
from pathlib import Path
from platform import node
from threading import Event, Thread
from time import sleep

import inquirer
from billiard.context import Process
from celery.apps.beat import Beat
from celery.apps.worker import Worker
from clear import clear
from socketio import AsyncServer  # noqa: F401
from termcolor import colored
from tqdm import tqdm
from uvicorn import Server  # noqa: F401

from crawjud.config import StoreThread, running_servers
from crawjud.core import create_app
from crawjud.core.watch import monitor_log
from crawjud.menu_manager import MenuManager
from crawjud.utils.gen_seed import worker_name_generator

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
                "Quart API ASGI": self.quart_menu_api,
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
