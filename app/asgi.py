"""module used to import the app module to the routes package."""

import os

from app import AppFactory

os.environ.update({
    "APPLICATION_APP": "quart",
    "IN_PRODUCTION": "True",
})

AppFactory.start_app()
