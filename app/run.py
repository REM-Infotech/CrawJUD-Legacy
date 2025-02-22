"""module used to import the app module to the routes package."""

import os

from app import AppFactory

os.environ.update({"APPLICATION_APP": "worker", "INTO_PRODUCTION": "False"})

_, app = AppFactory.construct_app()
