"""Blueprint for the Celery Beat server."""

import asyncio
from pathlib import Path

import clear
from billiard.context import Process
from termcolor import colored
from tqdm import tqdm

from server.config import StoreProcess, running_servers

from .io_client import io, watch_input


async def start() -> None:
    """Start the server."""
    celery_process = Process(target=start_beat)
    celery_process.start()

    store_process = StoreProcess(
        process_name="Beat",
        process_id=celery_process.pid,
        process_status="Running",
        process_object=celery_process,
    )

    running_servers["Beat"] = store_process

    return ["Server started.", "INFO", "green"]


async def restart() -> None:
    """Restart the server."""
    if not running_servers.get("Beat"):
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
    try:
        store_process: StoreProcess = running_servers.pop("Beat")
        if store_process:
            process_stop: Process = store_process.process_object
            process_stop.terminate()
            process_stop.join(15)

    except Exception as e:
        return [f"Error: {e}", "ERROR", "red"]


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Beat"):
        return ["Server not running.", "ERROR", "red"]

    clear()
    tqdm.write("Type 'ESC' to exit.")

    io.connect("http://localhost:7000", namespaces=["/beat"])
    while not watch_input():
        ...

    io.disconnect()

    return ["Exiting logs.", "INFO", "yellow"]


def start_beat() -> None:
    """Initialize and run the Celery beat scheduler."""
    import os

    from celery import Celery
    from celery.apps.beat import Beat
    from clear import clear
    from quart import Quart

    from api import AppFactory

    # Set environment variables to designate worker mode and production status.
    os.environ.update({
        "APPLICATION_APP": "beat",
    })

    # Create the Beat application and Celery instance via AppFactory.
    quart_app, app = AppFactory.construct_app()
    clear()

    async def run_beat(app: Celery, quart_app: Quart) -> None:
        """Run the Celery beat scheduler within the Beat application context.

        This function sets up the log file for beat scheduler output, ensures
        the logging directory exists, and starts the beat scheduler with a
        specified maximum interval and a custom database scheduler.

        Args:
            app (Celery): The Celery application instance.
            quart_app (Beat): The Beat application instance.

        """
        async with quart_app.app_context():
            # Define the path for the beat scheduler log file.
            logfile = str(Path(__file__).cwd().joinpath("logs", "beat.log"))
            # Ensure the directory for logs exists.
            Path(logfile).parent.mkdir(parents=True, exist_ok=True)
            # Create the log file if it does not already exist.
            Path(logfile).touch(exist_ok=True)
            # Initialize the beat scheduler with debug logging and custom scheduler.
            beat = Beat(
                app=app,
                loglevel="DEBUG",
                max_interval=10,
                scheduler="utils.scheduler:DatabaseScheduler",
                logfile=logfile,
            )
            beat.run()

    asyncio.run(run_beat(app, quart_app))
