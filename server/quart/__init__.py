"""Quart blueprint for the server."""

from pathlib import Path  # noqa: F401

from billiard.context import Process
from socketio import Client
from tqdm import tqdm

from server.config import StoreProcess, running_servers


async def status() -> None:
    """Log the status of the server."""
    if not running_servers.get("Quart"):
        tqdm.write("Server not running.")
        return

    io = Client()
    io.connect("http://localhost:7000")

    @io.on("quart_logs", namespace="/quart")
    async def quart_logs(data: dict[str, str]) -> None:
        tqdm.write(f"{data.get('message')}")

    while True:
        try:
            ...
        except KeyboardInterrupt:
            io.disconnect()
            break


async def shutdown() -> None:
    """Shutdown the server."""
    store_process: StoreProcess = running_servers.pop("Quart")
    if store_process:
        process_stop: Process = store_process.process_object
        process_stop.terminate()
        process_stop.join(15)


async def restart() -> None:
    """Restart the server."""
    await shutdown()
    await start()


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


def start_process_asgi() -> None:
    """Start the Quart server."""
    import os

    from clear import clear

    from app import AppFactory

    # Set environment variables to designate Quart app mode and production status.
    os.environ.update({
        "APPLICATION_APP": "quart",
    })

    clear()
    # Start the Quart application using the AppFactory.
    AppFactory.construct_app()
