"""ASGI blueprint for the server."""

from pathlib import Path  # noqa: F401

from billiard.context import Process

from server.config import StoreProcess, running_servers


async def shutdown() -> None:
    """Shutdown the ASGI server."""
    store_process: StoreProcess = running_servers.pop("ASGI")
    if store_process:
        process_stop: Process = store_process.process_object
        process_stop.terminate()
        process_stop.join(15)

    return  # await make_response(await render_template("index.html", message="Process stopped."))


async def restart() -> None:
    """Restart the ASGI server."""
    return  # await make_response(await render_template("index.html", page="restart.html"))


async def start() -> None:
    """Start the ASGI server."""
    asgi_process = Process(target=start_process_asgi)
    asgi_process.start()

    store_process = StoreProcess(
        process_name="ASGI",
        process_id=asgi_process.pid,
        process_status="Running",
        process_object=asgi_process,
    )

    running_servers["ASGI"] = store_process

    return


def start_process_asgi() -> None:
    """Start the ASGI server."""
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
