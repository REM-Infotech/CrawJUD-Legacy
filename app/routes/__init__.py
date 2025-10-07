"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import (
    Response,
    current_app,
    jsonify,
    make_response,
)
from flask import current_app as app
from flask_jwt_extended import jwt_required

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy

    from app.interfaces import HealtCheck


@app.route("/", methods=["GET"], websocket=True)
@jwt_required
def index() -> Response:
    """Redirect to the authentication login page.

    Returns:
        Response: A Quart redirect response to the login page.

    """
    return make_response(jsonify(message="ok"), 200)


@app.route("/api/health")
def health_check() -> HealtCheck:
    """Verifique status de saúde da aplicação.

    Returns:
        HealtCheck: HealtCheck

    """
    try:
        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        # Testa conexão com banco de dados
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "erro"

    return {
        "status": "ok" if db_status == "ok" else "erro",
        "database": db_status,
        "timestamp": str(db.func.now()),
    }
