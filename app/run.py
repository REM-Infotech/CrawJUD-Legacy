"""module used to import the app module to the routes package."""

from app import AppFactory

_, app = AppFactory.start_app()
