"""Run the server components in separate threads and allow stopping with an event."""

import asyncio
import logging
from os import environ, getcwd, getenv
from pathlib import Path
from platform import node
from queue import Queue  # noqa: F401
from threading import Condition, Thread, current_thread  # noqa: F401
from time import sleep as time_sleep
from typing import Any, TypeVar  # noqa: F401

from billiard.context import Process
from celery import Celery
from celery.apps.beat import Beat  # noqa: F401
from celery.apps.worker import Worker
from clear import clear
from pynput._util import AbstractListener  # noqa: F401
from quart import Quart
from rich.console import Console  # noqa: F401
from rich.live import Live  # noqa: F401
from rich.spinner import Spinner
from rich.text import Text  # noqa: F401
from socketio import ASGIApp
from uvicorn import Config, Server

from crawjud.core.config import StoreService, running_servers
from crawjud.core.configurator import get_hostname
from crawjud.core.watch import monitor_log
from crawjud.logs import log_cfg
from crawjud.types import app_name
from crawjud.utils.gen_seed import worker_name_generator

printf = Console().print


def sleep(numero: int = None) -> None:  # noqa: D103
    if environ.get("DEBUG", "False").lower() == "true":
        time_sleep(numero)


def start_worker() -> None:
    """Start the Celery beat scheduler."""
    from crawjud.core import create_app

    app, _, celery = asyncio.run(create_app())
    worker_name = f"{worker_name_generator()}@{node()}"
    environ.update({"APPLICATION_APP": "worker", "WORKER_NAME": worker_name})

    async def start_worker() -> None:
        async with app.app_context():
            worker = Worker(
                app=celery,
                hostname=worker_name,
                task_events=True,
                concurrency=16,
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
    from crawjud.core import create_app

    environ.update({"APPLICATION_APP": "beat"})

    async def beat_start() -> None:
        async with app.app_context():
            # beat = Beat(
            #     app=celery,
            #     scheduler="crawjud.utils.scheduler:DatabaseScheduler",
            #     max_interval=5,
            #     loglevel="INFO",
            #     logfile=Path(getcwd()).joinpath("crawjud", "logs", "beat_celery.log"),
            #     no_color=False,
            # )
            # beat.run()
            ...

    app, _, celery = asyncio.run(create_app())
    asyncio.run(beat_start())


class RunnerServices:
    """Run the server components in separate threads and allow stopping with an event."""

    celery_: Celery = None
    app_: Quart = None
    srv_: Server = None
    asgi_: ASGIApp = None
    worker_: Worker = None

    def start_quart(
        self,
    ) -> None:
        """Run the Quart server in a thread controlled by a stop event.

        Args:
            stop_event (Event): Event to signal the thread to stop.

        """
        log_file = Path(getcwd()).joinpath("crawjud", "logs", "uvicorn_api.log")
        cfg, _ = log_cfg(log_file=log_file)
        port = getenv("SERVER_PORT", 5000)
        hostname = getenv(
            "SERVER_HOSTNAME",
            get_hostname(),
        )

        log_level = logging.INFO
        if getenv("DEBUG", "False").lower() == "true":
            log_level = logging.INFO
        cfg = Config(
            self.asgi,
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

        asyncio.run(self.app.shutdown())
        asyncio.run(self.srv.shutdown())

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
                with Live(
                    Spinner(
                        name="dots",
                        text=f"[bold yellow]Starting {k} application[/bold yellow]",
                    ),
                    refresh_per_second=4,
                ) as live:
                    sleep(1)
                    running_servers.update({k: store})

                    if k == "Quart":
                        Thread(target=self.watch_shutdown, daemon=True).start()

                    store.start()
                    sleep(2)
                    live.update(
                        Text(
                            text=f"✅ {k} application started successfully!",
                            style="bold green",
                        )
                    )
                    sleep(2)
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
        if app_name == "Quart":
            self.start_quart()
        # elif app_name == "Worker":
        #     self.start_worker()
        # else:
        #     raise ValueError("Invalid app name.")

    def stop(self, app_name: app_name) -> None:
        """Stop the server."""
        if app_name == "Quart":
            asyncio.run(self.srv.shutdown())
        elif app_name == "Worker":
            self.worker.stop()
        else:
            raise ValueError("Invalid app name.")

    def restart(self, app_name: app_name) -> None:
        """Restart the server."""
        self.stop(app_name)
        self.start(app_name)

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

    @property
    def worker(self) -> Worker:
        """Return the worker process."""
        return self.worker_

    @worker.setter
    def worker(self, value: Worker) -> None:
        """Set the worker process."""
        self.worker_ = value
