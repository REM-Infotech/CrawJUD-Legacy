"""Blueprint for the worker server."""

import asyncio
import os
from pathlib import Path  # noqa: F401
from platform import node
from threading import Thread

from celery import Celery
from celery.apps.worker import Worker
from clear import clear
from quart import Quart
from termcolor import colored
from tqdm import tqdm

from crawjud.core.config import StoreService, running_servers
from crawjud.core.watch import monitor_log
from crawjud.utils import worker_name_generator


async def start() -> None:
    """Start the server."""
    if running_servers.get("Worker"):
        return ["Server already running.", "ERROR", "red"]

    celery_thread = Thread(target=start_worker, name="Worker Celery")
    celery_thread.start()

    return ["Server started.", "INFO", "green"]


async def restart() -> None:
    """Restart the server."""
    if not running_servers.get("Worker"):
        tqdm.write(colored("[INFO] Server not running. Starting server...", "yellow", attrs=["bold"]))
        asyncio.sleep(2)
        return await start()

    tqdm.write(colored("[INFO] Restarting server...", "yellow", attrs=["bold"]))

    await shutdown()
    await start()

    asyncio.sleep(2)

    return ["Server restarted.", "INFO", "green"]


async def shutdown() -> None:
    """Shutdown the server."""
    store_thread: StoreService = running_servers.get("Worker")
    if not store_thread:
        return ["Server not running.", "WARNING", "yellow"]

    try:
        store_thread: StoreService = running_servers.pop("Worker")
        if store_thread:
            thread_stop: Thread = store_thread.process_object

            thread_stop.join(15)

        tqdm.write(colored("[INFO] Server stopped.", "yellow", attrs=["bold"]))
        asyncio.sleep(2)

    except Exception as e:
        return [f"Error: {e}", "ERROR", "red"]


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Worker"):
        return ["Server not running.", "ERROR", "red"]

    clear()
    tqdm.write("Type 'ESC' to exit.")

    monitor_log("worker_celery.log")

    return ["Exiting logs.", "INFO", "yellow"]


def start_worker() -> None:
    """Initialize and run the Celery worker."""
    # Set environment variables to designate worker mode and production status.
    os.environ.update({
        "APPLICATION_APP": "worker",
    })

    # Create the Quart application and Celery instance via ApplicationFactory.

    async def run_worker(app: Celery, quart_app: Quart) -> None:
        """Run the Celery worker within the Quart application context.

        This function starts the Celery worker with detailed configurations,
        enabling task events, setting the log level, defining concurrency, and
        specifying the thread pool for execution.

        Args:
            app (Celery): The Celery application instance.
            quart_app (Quart): The Quart application instance.

        """
        os.environ.update({
            "APPLICATION_APP": "worker",
        })

        worker_name = f"{worker_name_generator()}@{node()}"
        async with quart_app.app_context():
            # Instantiate the worker with the app and specific settings.
            worker = Worker(
                app=app,
                hostname=worker_name,
                task_events=True,
                loglevel="INFO",
                concurrency=50.0,
                pool="threads",
            )
            worker.start()
