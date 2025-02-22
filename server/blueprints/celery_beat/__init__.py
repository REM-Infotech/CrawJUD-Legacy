"""Blueprint for the Celery Beat server."""

import asyncio
from pathlib import Path

from billiard.context import Process
from quart import Blueprint, Response, make_response, render_template

from server import StoreProcess, running_servers

template_folder = Path(__file__).parent.resolve().joinpath("templates")
static_folder = Path(__file__).parent.resolve().joinpath("static")
beat_ = Blueprint(
    "beat",
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),
    url_prefix="/beat",
)


@beat_.get("/status")
async def status() -> Response:
    """Check the status of the beat server."""
    return await make_response(await render_template("index.html", page="status.html"))


@beat_.post("/shutdown")
async def shutdown() -> Response:
    """Shutdown the beat server."""
    return await make_response(await render_template("index.html", page="shutdown.html"))


@beat_.get("/restart")
async def restart() -> Response:
    """Restart the beat server."""
    return await make_response(await render_template("index.html", page="restart.html"))


@beat_.get("/start")
async def start() -> Response:
    """Start the beat server."""
    beat_process = Process(target=start_beat)
    beat_process.start()

    store_process = StoreProcess(
        "celery_beat",
        beat_process.pid,
        "Running",
        beat_process,
    )
    running_servers["celery_beat"] = store_process

    return await make_response(
        await render_template(
            "index.html",
            page="start.html",
        )
    )


def start_beat() -> None:
    """Initialize and run the Celery beat scheduler."""
    import os
    from pathlib import Path

    from celery import Celery
    from celery.apps.beat import Beat
    from clear import clear
    from quart import Quart

    from app import AppFactory

    # Set environment variables to designate worker mode and production status.
    os.environ.update({
        "APPLICATION_APP": "worker",
    })

    # Create the Quart application and Celery instance via AppFactory.
    quart_app, app = AppFactory.construct_app()
    clear()
    if __name__ == "__main__":

        async def run_beat(app: Celery, quart_app: Quart) -> None:
            """Run the Celery beat scheduler within the Quart application context.

            This function sets up the log file for beat scheduler output, ensures
            the logging directory exists, and starts the beat scheduler with a
            specified maximum interval and a custom database scheduler.

            Args:
                app (Celery): The Celery application instance.
                quart_app (Quart): The Quart application instance.

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
