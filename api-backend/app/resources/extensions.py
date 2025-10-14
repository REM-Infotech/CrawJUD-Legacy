"""Extensões do App."""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from app.base import Model, Query

db = SQLAlchemy(model_class=Model, query_class=Query)  # pyright: ignore[reportArgumentType]
jwt = JWTManager()
mail = Mail()
cors = CORS(
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True,
    origins=[
        "localhost",
        "http://localhost:5173",
        "http://127.0.0.1:1473",
        "http://localhost:1474",  # Adiciona a origem necessária para evitar erro CORS
    ],
)

__all__ = ["db", "cors", "jwt", "mail", "start_extensions"]


def start_extensions(app: Flask) -> None:
    """Inicializa as extensões do Flask."""
    with app.app_context():
        global db
        db.init_app(app)
        cors.init_app(app)
        jwt.init_app(app)
        mail.init_app(app)
