"""Module for manage application with System Status and System Information."""

from dataclasses import dataclass
from pathlib import Path

from quart import Quart, Response, make_response, render_template

instance_dir = Path(__file__).parent.resolve().joinpath("instance")
template_dir = Path(__file__).parent.resolve().joinpath("templates")
static_dir = Path(__file__).parent.resolve().joinpath("static")

app = Quart(
    __name__,
    template_folder=str(template_dir),
    static_folder=str(static_dir),
    instance_path=str(instance_dir),
)


@dataclass
class StoreProcess:
    """Dataclass for storing process information."""

    process_name: str
    process_id: int
    process_status: str


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


def start_worker() -> None:
    """Initialize and run the Celery worker."""
    import asyncio
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


def start_beat() -> None:
    """Initialize and run the Celery beat scheduler."""
    import asyncio
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


@app.route("/dashboard")
async def dashboard() -> Response:
    """Render the dashboard template."""
    return await make_response(render_template("index.html", page="dashboard.html"))


async def register_blueprint() -> None:
    """Register the ASGI, worker, and beat blueprints."""
    async with app.app_context():
        from .blueprints import asgi_, beat_, worker_

        for blueprint_ in [asgi_, worker_, beat_]:
            app.register_blueprint(blueprint_)
