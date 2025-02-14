"""module used to import the app module to the routes package."""

import os

from celery.apps.worker import Worker

from app import AppFactory

os.environ.update({"APPLICATION_APP": "worker", "IN_PRODUCTION": "True"})

_, app = AppFactory.start_app()

if __name__ == "__main__":
    worker = Worker(app=app, task_events=True, loglevel="INFO", concurrency=50, pool="threads")
    worker.start()
