"""Database initialization and configuration module.

This module handles the database setup and initial configuration for the application.
It provides functionality to create and initialize the database, including setting up
the server information in the database.
"""

from pathlib import Path

import aiofiles
from quart import Quart

from crawjud.core import db


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
    from crawjud.models import init_database

    if not Path("is_init.txt").exists():
        async with aiofiles.open("is_init.txt", "w") as f:
            await f.write(f"{await init_database(app, db)}")

    from crawjud.models import Users

    if not db.engine.dialect.has_table(db.engine.connect(), Users.__tablename__):
        async with aiofiles.open("is_init.txt", "w") as f:
            await f.write(f"{await init_database(app, db)}")
