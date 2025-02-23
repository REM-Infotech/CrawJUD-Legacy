"""Blueprint for the worker server."""

import asyncio
from pathlib import Path  # noqa: F401

from billiard.context import Process
from socketio import Client
from tqdm import tqdm

from server.config import StoreProcess, running_servers


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Worker"):
        return ["Server not running.", "ERROR", "red"]

    tqdm.write("Type 'Ctrl+C' to exit.")

    io = Client()
    io.connect("http://localhost:7000")

    @io.on("worker_logs", namespace="/worker")
    async def quart_logs(data: dict[str, str]) -> None:
        tqdm.write(f"{data.get('message')}")

    while True:
        try:
            ...
        except KeyboardInterrupt:
            io.disconnect()
            break

    return ["Exiting logs.", "INFO", "yellow"]


async def shutdown() -> list[str]:
    """Shutdown the server."""
    store_process: StoreProcess = running_servers.pop("Worker")
    if store_process:
        process_stop: Process = store_process.process_object
        process_stop.terminate()
        process_stop.join(15)

    return ["Server closed.", "SUCCESS", "green"]


async def restart() -> list[str]:
    """Restart the server."""
    await shutdown()
    await start()

    return ["Server restarted.", "INFO", "yellow"]


async def start() -> list[str]:
    """Start the server."""
    asgi_process = Process(target=start_worker)
    asgi_process.start()

    store_process = StoreProcess(
        process_name="Worker",
        process_id=asgi_process.pid,
        process_status="Running",
        process_object=asgi_process,
    )

    running_servers["Worker"] = store_process

    return ["Server started.", "SUCCESS", "green"]


def start_worker() -> None:
    """Initialize and run the Celery worker."""
    import os
    from platform import node

    from celery import Celery
    from celery.apps.worker import Worker
    from clear import clear
    from quart import Quart

    from app import AppFactory
    from utils import worker_name_generator

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
