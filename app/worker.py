"""Module for initializing and running the Celery worker.

This module configures the environment, initializes the Quart and Celery
applications using AppFactory, and starts a Celery worker with specified
settings such as task events, log level, concurrency, and thread pool.
"""

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

if not os.environ.get("CONTAINER_DOCKER_APP"):
    os.environ.update({
        "IN_PRODUCTION": "True",
    })

# Create the Quart application and Celery instance via AppFactory.
quart_app, app = AppFactory.construct_app()
clear()
if __name__ == "__main__":

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
