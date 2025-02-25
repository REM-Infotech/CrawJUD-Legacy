"""Quart blueprint for the server."""

from pathlib import Path  # noqa: F401

import keyboard  # type: ignore # noqa: PGH003
from billiard.context import Process
from tqdm import tqdm

from server.config import StoreProcess, running_servers

from .io_client import io


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Quart"):
        return ["Server not running.", "ERROR", "red"]

    tqdm.write("Type 'E' to exit.")

    io.connect("http://localhost:7000", namespaces=["/quart_web"])
    while True:
        if keyboard.read_key().lower() == "e":
            break
    io.disconnect()

    return ["Exiting logs.", "INFO", "yellow"]


async def shutdown() -> None:
    """Shutdown the server."""
    try:
        store_process: StoreProcess = running_servers.pop("Quart")
        if store_process:
            process_stop: Process = store_process.process_object
            process_stop.terminate()
            process_stop.join(15)

    except Exception as e:
        return [f"Error: {e}", "ERROR", "red"]


async def restart() -> None:
    """Restart the server."""
    await shutdown()
    await start()

    return ["Server restarted.", "INFO", "green"]


async def start() -> None:
    """Start the server."""
    asgi_process = Process(target=start_process_asgi)
    asgi_process.start()

    store_process = StoreProcess(
        process_name="Quart",
        process_id=asgi_process.pid,
        process_status="Running",
        process_object=asgi_process,
    )

    running_servers["Quart"] = store_process

    return ["Server started.", "INFO", "green"]


def start_process_asgi() -> None:
    """Start the Quart server."""
    import os

    from clear import clear

    from web import AppFactory

    # Set environment variables to designate Quart app mode and production status.
    os.environ.update({
        "APPLICATION_APP": "quart_web",
    })

    clear()
    # Start the Quart application using the AppFactory.
    AppFactory.construct_app()
