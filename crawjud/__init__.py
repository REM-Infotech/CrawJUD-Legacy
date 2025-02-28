"""Main module for the CrawJUD Package."""

import asyncio
from os import environ
from pathlib import Path
from platform import node
from threading import Thread
from time import sleep
from typing import Callable, Dict

import inquirer
import rich
from billiard.context import Process
from celery.apps.beat import Beat
from celery.apps.worker import Worker
from clear import clear
from socketio import AsyncServer
from termcolor import colored
from tqdm import tqdm

from crawjud.config import StoreService, running_servers
from crawjud.core import create_app
from crawjud.crawjud_manager import HeadCrawjudManager
from crawjud.types import app_name
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

    environ.update({"APPLICATION_APP": "beat"})

    async def beat_start() -> None:
        async with app.app_context():
            beat = Beat(
                app=celery,
                scheduler="crawjud.utils.scheduler:DatabaseScheduler",
                quiet=True,
            )
            beat.run()

    app, _, celery = asyncio.run(create_app())
    asyncio.run(beat_start())


def start_worker() -> None:
    """Start the Celery beat scheduler."""
    from crawjud.core import create_app

    app, _, celery = asyncio.run(create_app())
    environ.update({"APPLICATION_APP": "worker"})

    async def start_worker() -> None:
        async with app.app_context():
            worker_name = f"{worker_name_generator()}@{node()}"
            worker = Worker(
                app=celery,
                hostname=worker_name,
                task_events=True,
                loglevel="INFO",
                concurrency=50.0,
                pool="threads",
            )
            worker = worker

            try:
                worker.start()

            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    worker.stop()

                else:
                    tqdm.write(
                        colored(
                            f"{colored('[ERROR]', 'red', attrs=['bold', 'blink'])} {e}",
                            "red",
                            attrs=["bold"],
                        )
                    )

    asyncio.run(start_worker())


class MasterApp(HeadCrawjudManager):
    """Master application class."""

    loop_app = True

    def boot_app(self) -> None:
        """Boot Beat and the application."""
        rich.print("[bold green]Starting application object...[/bold green]")
        self.app, self.asgi, self.celery = asyncio.run(create_app())

        process_beat = Process(target=start_beat, daemon=True)
        process_worker = Process(target=start_worker, daemon=True)

        running_servers["Worker"] = StoreService(
            process_name="Worker",
            process_object=process_worker,
            process_id=process_worker.pid,
        )
        running_servers["Beat"] = StoreService(
            process_name="Beat",
            process_object=process_beat,
            process_id=process_beat.pid,
        )
        process_worker.start()
        process_beat.start()

    def __init__(self) -> None:
        """Initialize the ASGI server."""
        self.boot_app()
        self.current_menu = self.main_menu
        self.current_menu_name = "Main Menu"

    @property
    def functions(
        self,
    ) -> dict[
        str,
        Callable[[app_name], None],
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
        clear()

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
                if choice == "Start Services":
                    call_obj = options.get(choice)
                    Thread(target=call_obj, daemon=True).start()
                elif choice != "Start Services":
                    options.get(choice)()

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

        self.return_main_menu()

    def return_main_menu(self) -> None:
        """Return to the main menu."""
        self.current_menu = self.main_menu
        self.current_menu_name = "Main Menu"
        self.current_choice = ""
        self.current_app = ""

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
            from crawjud.core.watch import monitor_log

            monitor_log(file_path=file_path)
            tqdm.write(colored("[INFO] Log file closed.", "yellow", attrs=["bold"]))
            sleep(2)
            clear()
            return

        tqdm.write(colored(f"[ERROR] File '{text_choice}' does not exist.", "red", attrs=["bold"]))
        sleep(2)
        clear()
