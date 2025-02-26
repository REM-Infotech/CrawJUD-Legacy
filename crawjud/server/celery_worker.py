"""Blueprint for the worker server."""

import asyncio
from pathlib import Path  # noqa: F401

import clear
from billiard.context import Process
from termcolor import colored
from tqdm import tqdm

from crawjud.server.config import StoreProcess, running_servers

from .io_client import io, watch_input


async def start() -> None:
    """Start the server."""
    celery_process = Process(target=start_worker)
    celery_process.start()

    store_process = StoreProcess(
        process_name="Worker",
        process_id=celery_process.pid,
        process_status="Running",
        process_object=celery_process,
    )

    running_servers["Worker"] = store_process

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
    store_process: StoreProcess = running_servers.get("Worker")
    if not store_process:
        return ["Server not running.", "WARNING", "yellow"]

    try:
        store_process: StoreProcess = running_servers.pop("Worker")
        if store_process:
            process_stop: Process = store_process.process_object
            process_stop.terminate()
            process_stop.join(15)

        tqdm.write(colored("[INFO] Server stopped.", "yellow", attrs=["bold"]))

    except Exception as e:
        return [f"Error: {e}", "ERROR", "red"]


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Worker"):
        return ["Server not running.", "ERROR", "red"]

    clear()
    tqdm.write("Type 'ESC' to exit.")

    io.connect("http://localhost:7000", namespaces=["/worker"])
    while not watch_input():
        ...

    io.disconnect()

    return ["Exiting logs.", "INFO", "yellow"]


def start_worker() -> None:
    """Initialize and run the Celery worker."""
    import os
    from platform import node

    from celery import Celery
    from celery.apps.worker import Worker
    from clear import clear
    from quart import Quart

    from crawjud.api import AppFactory
    from crawjud.utils import worker_name_generator

    # Set environment variables to designate worker mode and production status.
    os.environ.update({
        "APPLICATION_APP": "worker",
    })

    # Create the Quart application and Celery instance via AppFactory.
    quart_app, app = AppFactory.construct_app()
    clear()

    async def run_worker(app: Celery, quart_app: Quart) -> None:
        """Run the Celery worker within the Quart application context.

        This function starts the Celery worker with detailed configurations,
        enabling task events, setting the log level, defining concurrency, and
        specifying the thread pool for execution.

        Args:
            app (Celery): The Celery application instance.
            quart_app (Quart): The Quart application instance.

        """
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

    asyncio.run(run_worker(app, quart_app))
