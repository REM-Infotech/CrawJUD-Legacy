"""Run the server components in separate threads and allow stopping with an event."""

from platform import node
from threading import Thread

from celery.apps.worker import Worker
from clear import clear
from termcolor import colored
from tqdm import tqdm

from crawjud._types import app_name
from crawjud._utils.gen_seed import worker_name_generator
from crawjud.config import StoreThread, running_servers
from crawjud.core.watch import monitor_log


class RunnerServices:
    """Run the server components in separate threads and allow stopping with an event."""

    def start_worker(
        self,
    ) -> None:
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
        self.worker = worker
        worker.start()

    def start_quart(
        self,
    ) -> None:
        """Run the Quart server in a thread controlled by a stop event.

        Args:
            stop_event (Event): Event to signal the thread to stop.

        """
        self.srv.run()

    def start_all(self) -> None:
        """Start all server components in separate threads and allow stopping with an event.

        This method creates threads for the worker, Quart server, and Celery beat.
        It listens for a keyboard interrupt and then signals all threads to stop.
        """
        store_quart_thread = StoreThread(
            process_name="Quart",
            process_status="Running",
            process_object=Thread(target=self.start_quart),
        )

        store_thread_worker = StoreThread(
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
        if not running_servers.get(app_name):
            return ["Server not running.", "ERROR", "red"]

        clear()
        tqdm.write("Type 'ESC' to exit.")

        monitor_log("uvicorn_api.log")

        return ["Exiting logs.", "INFO", "yellow"]
