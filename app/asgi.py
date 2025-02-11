"""module used to import the app module to the routes package."""

import os

from app import AppFactory

os.environ.setdefault("APPLICATION_APP", "quart")

_, app = AppFactory.start_app()
