"""Database initialization and configuration module.

This module handles the database setup and initial configuration for the application.
It provides functionality to create and initialize the database, including setting up
the server information in the database.
"""

from os import getenv
from platform import system

from quart import Quart

from crawjud_bots.api import db


async def database_start(app: Quart) -> None:
    """Initialize and configure the application database.

    This function performs the following tasks:
    1. Checks if the current server exists in the database
    2. Creates a new server entry if it doesn't exist
    3. Initializes all database tables

    Args:
        app (Quart): The Quart application instance

    Returns:
        None

    Note:
        This function requires the following environment variables:
        - NAMESERVER: The name of the server
        - HOSTNAME: The address of the server

    """
    from crawjud_bots.api.models import Servers

    if not Servers.query.filter(Servers.name == getenv("NAMESERVER")).first():  # pragma: no cover
        server = Servers(name=getenv("NAMESERVER"), address=getenv("HOSTNAME"), system=system())
        db.session.add(server)
        db.session.commit()

    # Create the database.
    db.create_all()
