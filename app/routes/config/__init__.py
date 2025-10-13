"""Config blueprint for admin routes."""

from __future__ import annotations

from quart import Blueprint

admin = Blueprint("admin", __name__)


def import_routes() -> None:
    """Import routes."""
    from app.routes.config import users

    return users


import_routes()
