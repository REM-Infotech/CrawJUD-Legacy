"""module used to import the app module to the routes package."""

import os

from app import AppFactory

os.environ.update({"APPLICATION_APP": "beat", "IN_PRODUCTION": "True"})

_, app = AppFactory.start_app()
