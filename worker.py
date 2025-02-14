"""module used to import the app module to the routes package."""

import asyncio
import os

from celery import Celery
from celery.apps.worker import Worker
from quart import Quart

from app import AppFactory

os.environ.update({"APPLICATION_APP": "worker", "IN_PRODUCTION": "True"})

quart_app, app = AppFactory.start_app()

if __name__ == "__main__":

    async def run_worker(app: Celery, quart_app: Quart) -> None:
        """Run the worker."""
        async with quart_app.app_context():
            worker = Worker(app=app, task_events=True, loglevel="INFO", concurrency=50, pool="threads")
            worker.start()

    asyncio.run(run_worker(app, quart_app))
