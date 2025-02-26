"""Quart blueprint for the server web."""

import asyncio
from pathlib import Path  # noqa: F401
from threading import Thread

from clear import clear
from termcolor import colored
from tqdm import tqdm

from crawjud.server.config import StoreThread, running_servers

from .watch import monitor_log


async def start() -> None:
    """Start the server."""
    if running_servers.get("Quart Web"):
        return ["Server already running.", "ERROR", "red"]

    asgi_process = Thread(target=start_process_asgi, name="Quart Web")
    asgi_process.start()

    store_process = StoreThread(
        process_name="Quart Web",
        process_id=asgi_process.ident,
        process_status="Running",
        process_object=asgi_process,
    )

    running_servers["Quart Web"] = store_process

    return ["Server started.", "INFO", "green"]


async def restart() -> None:
    """Restart the server."""
    if not running_servers.get("Quart Web"):
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
    store_process: StoreThread = running_servers.get("Quart Web")
    if not store_process:
        return ["Server not running.", "WARNING", "yellow"]

    try:
        store_process: StoreThread = running_servers.pop("Quart Web")
        if store_process:
            thread_stop: Thread = store_process.process_object

            thread_stop.join(15)

        tqdm.write(colored("[INFO] Server stopped.", "yellow", attrs=["bold"]))
        asyncio.sleep(2)

    except Exception as e:
        return [f"Error: {e}", "ERROR", "red"]


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Quart Web"):
        return ["Server not running.", "ERROR", "red"]

    clear()
    tqdm.write("Type 'ESC' to exit.")

    monitor_log("uvicorn_web.log")

    return ["Exiting logs.", "INFO", "yellow"]


def start_process_asgi() -> None:
    """Start the Quart server."""
    import os

    from crawjud.web import AppFactory

    # Set environment variables to designate Quart app mode and production status.
    os.environ.update({
        "APPLICATION_APP": "quart_web",
    })
    # Start the Quart application using the AppFactory.
    AppFactory.construct_app()
