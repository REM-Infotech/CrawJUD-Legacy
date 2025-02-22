"""Blueprint for the worker server."""

import asyncio
from pathlib import Path

from billiard.context import Process
from quart import Blueprint, Response, make_response, render_template

from server import StoreProcess, running_servers

template_folder = Path(__file__).parent.resolve().joinpath("templates")
static_folder = Path(__file__).parent.resolve().joinpath("static")
worker_ = Blueprint(
    "worker",
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),
    url_prefix="/worker",
)


@worker_.get("/status")
async def status() -> Response:
    """Check the status of the worker server."""
    return await make_response(await render_template("index.html", page="status.html"))


@worker_.post("/shutdown")
async def shutdown() -> Response:
    """Shutdown the worker server."""
    return await make_response(await render_template("index.html", page="shutdown.html"))


@worker_.get("/restart")
async def restart() -> Response:
    """Restart the worker server."""
    return await make_response(await render_template("index.html", page="restart.html"))


@worker_.get("/start")
async def start() -> Response:
    """Start the worker server."""
    worker_process = Process(target=start_worker)
    worker_process.start()

    store_process = StoreProcess(
        "celery_worker",
        worker_process.pid,
        "Running",
        worker_process,
    )

    running_servers["celery_worker"] = store_process

    return await make_response(
        await render_template(
            "index.html",
            message="Process started.",
        )
    )


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
