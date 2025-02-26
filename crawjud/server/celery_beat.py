"""Blueprint for the Celery Beat server."""

import asyncio

from billiard.context import Process
from clear import clear
from termcolor import colored
from tqdm import tqdm

from crawjud.server.config import StoreProcess, running_servers

from .watch import monitor_log


async def start() -> None:
    """Start the server."""
    if running_servers.get("Beat"):
        return ["Server already running.", "ERROR", "red"]

    celery_process = Process(target=start_beat, name="Beat Celery")
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

        tqdm.write(colored("[INFO] Server stopped.", "yellow", attrs=["bold"]))
        asyncio.sleep(2)

    except Exception as e:
        return [f"Error: {e}", "ERROR", "red"]


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Beat"):
        return ["Server not running.", "ERROR", "red"]

    clear()
    tqdm.write("Type 'ESC' to exit.")

    monitor_log("beat_celery.log")
    return ["Exiting logs.", "INFO", "yellow"]


def start_beat() -> None:
    """Initialize and run the Celery beat scheduler."""
    import os

    from celery import Celery
    from celery.apps.beat import Beat
    from quart import Quart

    from crawjud.api import AppFactory

    # Set environment variables to designate worker mode and production status.
    os.environ.update({
        "APPLICATION_APP": "beat",
    })

    # Create the Beat application and Celery instance via AppFactory.
    quart_app, app = AppFactory.construct_app()

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
            beat = Beat(
                app=app,
                scheduler="crawjud.utils.scheduler:DatabaseScheduler",
            )
            beat.run()

    asyncio.run(run_beat(app, quart_app))
