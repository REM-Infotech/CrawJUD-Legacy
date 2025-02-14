"""module used to import the app module to the routes package."""

import os

from celery.apps.beat import Beat

from app import AppFactory

os.environ.update({"APPLICATION_APP": "worker", "IN_PRODUCTION": "True"})

_, app = AppFactory.start_app()

if __name__ == "__main__":
    beat = Beat(app=app, loglevel="INFO", max_interval=10)
    beat.start()
