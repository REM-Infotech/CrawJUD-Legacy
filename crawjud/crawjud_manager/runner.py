"""Run the server components in separate threads and allow stopping with an event."""

import asyncio
import logging
from os import getcwd, getenv
from pathlib import Path
from threading import Thread

from celery import Celery
from celery.apps.worker import Worker
from clear import clear
from quart import Quart
from socketio import ASGIApp
from termcolor import colored
from tqdm import tqdm
from uvicorn import Config, Server

from crawjud.config import StoreService, running_servers
from crawjud.core.configurator import get_hostname
from crawjud.core.watch import monitor_log
from crawjud.logs import log_cfg
from crawjud.types import app_name


class RunnerServices:
    """Run the server components in separate threads and allow stopping with an event."""

    celery_: Celery = None
    app_: Quart = None
    srv_: Server = None
    asgi_: ASGIApp = None
    worker_: Worker = None

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
            log_level = logging.DEBUG
        cfg = Config(
            self.asgi,
            host=hostname,
            port=port,
            log_config=cfg,
            log_level=log_level,
        )
        self.srv = Server(cfg)
        self.srv.run()

    def start_all(self) -> None:
        """Start all server components in separate threads and allow stopping with an event.

        This method creates threads for the worker, Quart server, and Celery beat.
        It listens for a keyboard interrupt and then signals all threads to stop.
        """
        store_quart_thread = StoreService(
            process_name="Quart",
            process_status="Running",
            process_object=Thread(target=self.start_quart),
        )

        store_thread_worker = StoreService(
            process_name="Worker",
            process_status="Running",
            process_object=Thread(target=self.start_worker),
        )

        running_servers.update({
            "Quart": store_quart_thread,
            "Worker": store_thread_worker,
        })

        store_thread_worker.start()
        store_quart_thread.start()

        tqdm.write(colored("[INFO] All servers started.", "green", attrs=["bold"]))

    def status(self, app_name: app_name) -> None:
        """Log the status of the server."""
        if not running_servers.get(app_name.capitalize()):
            return ["Server not running.", "ERROR", "red"]

        clear()
        tqdm.write("Type 'ESC' to exit.")

        monitor_log("uvicorn_api.log")

        return ["Exiting logs.", "INFO", "yellow"]

    def start(self, app_name: app_name) -> None:
        """Start the server."""
        if app_name == "Quart":
            self.start_quart()
        elif app_name == "Worker":
            self.start_worker()
        else:
            raise ValueError("Invalid app name.")

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
