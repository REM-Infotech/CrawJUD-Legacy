"""Database initialization and configuration module.

This module provides functionality to initialize and configure the application's
database connection, create necessary tables, and ensure basic server information
is recorded in the database.

Attributes:
    None

"""

from os import getenv
from platform import system

from quart import Quart

from app import db


async def database_start(app: Quart) -> None:
    """Initialize and configure the application database.

    This function performs the following operations:
    1. Checks if the current server exists in the database
    2. Creates a new server entry if it doesn't exist
    3. Initializes all database tables

    Args:
        app (Quart): The Quart application instance.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there's an error communicating with the database.

    """
    from app.models import Servers

    if not Servers.query.filter(Servers.name == getenv("NAMESERVER")).first():  # pragma: no cover
        server = Servers(name=getenv("NAMESERVER"), address=getenv("HOSTNAME"), system=system())
        db.session.add(server)
        db.session.commit()

    # Create the database.
    db.create_all()
