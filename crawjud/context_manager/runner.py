"""Run the server components in separate threads and allow stopping with an event."""

from platform import node
from threading import Thread

from celery.apps.worker import Worker
from clear import clear
from tqdm import tqdm

from crawjud.config import StoreThread, running_servers
from crawjud.core.watch import monitor_log
from crawjud.utils.gen_seed import worker_name_generator


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
        Thread(target=worker.start, name="Worker Celery").start()
        worker.stop()

    def start_quart(
        self,
    ) -> None:
        """Run the Quart server in a thread controlled by a stop event.

        Args:
            stop_event (Event): Event to signal the thread to stop.

        """

    def start_all(self) -> None:
        """Start all server components in separate threads and allow stopping with an event.

        This method creates threads for the worker, Quart server, and Celery beat.
        It listens for a keyboard interrupt and then signals all threads to stop.
        """
        worker_thread = Thread(target=self.start_worker)
        quart_thread = Thread(target=self.start_quart)

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
