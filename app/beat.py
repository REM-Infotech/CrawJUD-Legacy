"""module used to import the app module to the routes package."""

import asyncio
import os
from pathlib import Path

from celery import Celery
from celery.apps.beat import Beat
from quart import Quart

from app import AppFactory

os.environ.update({"APPLICATION_APP": "worker", "IN_PRODUCTION": "True"})

quart_app, app = AppFactory.start_app()

if __name__ == "__main__":

    async def run_beat(app: Celery, quart_app: Quart) -> None:
        """Run the beat scheduler."""
        async with quart_app.app_context():
            logfile = str(Path(__file__).cwd().joinpath("logs", "beat.log"))
            Path(logfile).parent.mkdir(parents=True, exist_ok=True)
            Path(logfile).touch(exist_ok=True)
            beat = Beat(
                app=app,
                loglevel="DEBUG",
                max_interval=10,
                scheduler="utils.scheduler:DatabaseScheduler",
                logfile=logfile,
            )
            beat.run()

    asyncio.run(run_beat(app, quart_app))
