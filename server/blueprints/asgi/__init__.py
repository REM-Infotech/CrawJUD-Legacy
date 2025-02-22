"""ASGI blueprint for the server."""

from pathlib import Path

from billiard.context import Process
from quart import Blueprint, Response, make_response, render_template

from ... import StoreProcess, running_servers

template_folder = Path(__file__).parent.resolve().joinpath("templates")
static_folder = Path(__file__).parent.resolve().joinpath("static")
asgi_ = Blueprint(
    "asgi",
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),
    url_prefix="/asgi",
)


@asgi_.get("/status")
async def status() -> Response:
    """Check the status of the ASGI server."""
    return await make_response(await render_template("status.html"))


@asgi_.get("/shutdown")
async def shutdown() -> Response:
    """Shutdown the ASGI server."""
    store_process: StoreProcess = running_servers.pop("ASGI")
    if store_process:
        process_stop: Process = store_process.process_object
        process_stop.terminate()
        process_stop.join(15)

    return await make_response(await render_template("index.html", message="Process stopped."))


@asgi_.get("/restart")
async def restart() -> Response:
    """Restart the ASGI server."""
    return await make_response(await render_template("index.html", page="restart.html"))


@asgi_.get("/start")
async def start() -> Response:
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

    return await make_response(
        await render_template(
            "index.html",
            message="Process started.",
        )
    )


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
