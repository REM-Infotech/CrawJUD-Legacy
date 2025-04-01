"""Blueprint for the Celery Beat server."""

import asyncio
from threading import Thread

from celery import Celery
from celery.apps.beat import Beat
from clear import clear
from quart import Quart
from termcolor import colored
from tqdm import tqdm

from api.config import StoreService, running_servers
from crawjud.utils.watch import monitor_log


async def start() -> None:
    """Start the server."""
    if running_servers.get("Beat"):
        return ["Server already running.", "ERROR", "red"]

    celery_thread = Thread(target=start_beat, name="Beat Celery")
    celery_thread.start()

    store_thread = StoreService(
        process_name="Beat",
        process_id=celery_thread.ident,
        process_status="Running",
        process_object=celery_thread,
    )

    running_servers["Beat"] = store_thread

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
        store_thread: StoreService = running_servers.pop("Beat")
        if store_thread:
            thread_stop: Thread = store_thread.process_object

            thread_stop.join(15)

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

    # Set environment variables to designate worker mode and production status.
    os.environ.update({
        "APPLICATION_APP": "beat",
    })

    # Create the Beat application and Celery instance via ApplicationFactory.

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
