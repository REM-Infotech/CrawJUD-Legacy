"""Module for launching the ASGI application.

This module sets environment variables necessary for running the Quart
application in production mode and initiates the application using AppFactory.
"""

import os

from clear import clear

from app import AppFactory

# Set environment variables to designate Quart app mode and production status.
os.environ.update({
    "APPLICATION_APP": "quart",
})


clear()
# Start the Quart application using the AppFactory.
AppFactory.construct_app()
