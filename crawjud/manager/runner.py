"""Run the server components in separate threads and allow stopping with an event."""

import asyncio
import logging
from os import environ, getcwd, getenv
from pathlib import Path
from platform import node
from queue import Queue  # noqa: F401
from threading import Condition, Event, Thread, current_thread  # noqa: F401
from time import sleep
from typing import Any, TypeVar  # noqa: F401

from billiard.context import Process  # noqa: F401
from celery import Celery
from celery.apps.beat import Beat  # noqa: F401
from celery.apps.worker import Worker
from clear import clear
from pynput._util import AbstractListener  # noqa: F401
from quart import Quart
from rich.console import Console  # noqa: F401
from rich.live import Live  # noqa: F401
from rich.text import Text  # noqa: F401
from socketio import ASGIApp
from uvicorn.config import Config
from uvicorn.server import Server

from api import app
from api.config import StoreService, running_servers
from crawjud.types import app_name
from crawjud.utils import worker_name_generator
from crawjud.utils.watch import monitor_log
from logs import log_cfg

printf = Console().print


def start_worker() -> None:
    """Start the Celery beat scheduler."""
    from crawjud import create_celery_app

    celery = asyncio.run(create_celery_app())
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
                    printf("[bold red]Error starting worker.")

    asyncio.run(start_worker())


def start_beat() -> None:
    """Start the Celery beat scheduler."""
    from crawjud import create_celery_app

    environ.update({"APPLICATION_APP": "beat"})

    async def beat_start() -> None:
        async with app.app_context():
            beat = Beat(
                app=celery,
                scheduler="crawjud.utils.scheduler:DatabaseScheduler",
                max_interval=5,
                loglevel="INFO",
                logfile=Path(getcwd()).joinpath("logs", "beat_celery.log"),
                no_color=False,
            )
            beat.run()

    celery = asyncio.run(create_celery_app())
    asyncio.run(beat_start())


class RunnerServices:
    """Run the server components in separate threads and allow stopping with an event."""

    _event_stop: Event = None
    celery_: Celery = None
    app_: Quart = None
    srv_ = None
    asgi_: ASGIApp = None
    worker_: Worker = None

    def start_quart(
        self,
    ) -> None:
        """Run the Quart server in a thread controlled by a stop event.

        Args:
            stop_event (Event): Event to signal the thread to stop.

        """
        log_file = Path(getcwd()).joinpath("logs", "uvicorn_api.log")
        cfg, _ = log_cfg(log_file=log_file)
        port = getenv("SERVER_PORT", 5000)
        hostname = "0.0.0.0"  # noqa: S104

        log_level = logging.INFO
        if getenv("DEBUG", "False").lower() == "true":
            log_level = logging.DEBUG
        cfg = Config(
            self.app,
            host=hostname,
            port=port,
            log_config=cfg,
            log_level=log_level,
        )
        self.srv = Server(cfg)
        Thread(target=self.srv.run, daemon=True).start()

    def watch_shutdown(self) -> None:
        """Watch for a keyboard interrupt and signal all threads to stop."""
        self.event_stop.wait()
        self.event_stop.set()

        if isinstance(self.app, ASGIApp):
            app: Quart = self.app.other_asgi_app
            asyncio.run(app.shutdown())
        else:
            asyncio.run(self.app.shutdown())

        asyncio.run(self.srv.shutdown())

    def start_specific(self, **kwargs: str) -> None:
        """Start all server components in separate threads and allow stopping with an event.

        This method creates threads for the worker, Quart server, and Celery beat.
        It listens for a keyboard interrupt and then signals all threads to stop.
        """
        start_dict = {}
        server_list = [kwargs.get("server")]

        if "," in kwargs.get("server"):
            server_list = kwargs.get("server").split(",")

        for server in server_list:
            start_dict.update({server: "True"})

        to_start = {
            "Quart": StoreService(
                process_name="Quart",
                process_status="Running",
                process_object=Thread(target=self.start_quart, daemon=True),
                process_log_file="uvicorn_api.log",
            ),
            "Beat": StoreService(
                process_name="Beat",
                process_status="Running",
                process_object=Process(target=start_beat, daemon=True),
                process_log_file="beat_celery.log",
            ),
            "Worker": StoreService(
                process_name="Worker",
                process_status="Running",
                process_object=Process(target=start_worker, daemon=True),
                process_log_file="worker_celery.log",
            ),
        }
        for k, store in to_start.items():
            if not running_servers.get(k) and start_dict.get(k):
                running_servers.update({k: store})
                store.start()

        clear()
        printf(Text("✅ All Application server started successfully", style="bold green"))
        sleep(2)
        clear()

    def start_all(self) -> None:
        """Start all server components in separate threads and allow stopping with an event.

        This method creates threads for the worker, Quart server, and Celery beat.
        It listens for a keyboard interrupt and then signals all threads to stop.
        """
        clear()
        to_start = {
            "Quart": StoreService(
                process_name="Quart",
                process_status="Running",
                process_object=Thread(target=self.start_quart, daemon=True),
                process_log_file="uvicorn_api.log",
            ),
            "Beat": StoreService(
                process_name="Beat",
                process_status="Running",
                process_object=Process(target=start_beat, daemon=True),
                process_log_file="beat_celery.log",
            ),
            "Worker": StoreService(
                process_name="Worker",
                process_status="Running",
                process_object=Process(target=start_worker, daemon=True),
                process_log_file="worker_celery.log",
            ),
        }

        for k, store in to_start.items():
            if not running_servers.get(k):
                running_servers.update({k: store})
                sleep(1)

                if k == "Quart":
                    Thread(target=self.watch_shutdown, daemon=True).start()

                store.start()

        clear()
        printf(Text("✅ All Application server started successfully", style="bold green"))
        sleep(2)
        clear()

    def status(self, app_name: app_name) -> None:
        """Log the status of the server."""
        if not running_servers.get(app_name.capitalize()):
            return ["Server not running.", "ERROR", "red"]

        clear()

        log_file = running_servers[app_name.capitalize()].process_log_file
        printf("[bold yellow]Type 'ESC' to exit.")

        monitor_log(file_name=log_file)

        return ["Exiting logs.", "INFO", "yellow"]

    def start(self, app_name: app_name) -> None:
        """Start the server."""
        app_ = app_name.capitalize()
        if app_ == "Quart":
            to_start = {
                "Quart": StoreService(
                    process_name="Quart",
                    process_status="Running",
                    process_object=Thread(target=self.start_quart, daemon=True),
                    process_log_file="hypercorn_api.log",
                )
            }

        elif app_ == "Worker":
            to_start = {
                "Worker": StoreService(
                    process_name="Worker",
                    process_status="Running",
                    process_object=Process(target=start_worker, daemon=True),
                    process_log_file="worker_celery.log",
                ),
            }

        elif app_ == "Beat":
            to_start = {
                "Beat": StoreService(
                    process_name="Beat",
                    process_status="Running",
                    process_object=Process(target=start_beat, daemon=True),
                    process_log_file="beat_celery.log",
                ),
            }

        to_start.get(app_).start()
        running_servers.update(to_start)
        return [f"{app_} started successfuly!", "SUCCESS", "green"]

    def stop(self, app_name: app_name) -> None:
        """Stop the server."""
        app_ = app_name.capitalize()
        if app_ == "Quart":
            self.event_stop.set()
            sleep(2)
            running_servers.pop(app_)
        elif app_ == "Worker":
            celery_app = running_servers.pop(app_)
            celery_app.process_object.terminate()

        elif app_ == "Beat":
            celery_app = running_servers.pop(app_)
            celery_app.process_object.terminate()

    def restart(self, app_name: app_name) -> None:
        """Restart the server."""
        self.stop(app_name)
        self.start(app_name)

    @property
    def event_stop(self) -> Event:
        """Return the event stop."""
        return self._event_stop

    @event_stop.setter
    def event_stop(self, value: Event) -> None:
        """Set the event stop."""
        self._event_stop = value
