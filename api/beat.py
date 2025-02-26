"""Module for initializing and running the Celery beat scheduler.

This module configures the environment, sets up logging for the beat scheduler,
and starts the scheduler with a custom database scheduler and debug log level.
"""

import asyncio
import os
from pathlib import Path

from celery import Celery
from celery.apps.beat import Beat
from clear import clear
from quart import Quart

from api import AppFactory

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
