"""Extensões do App."""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cors = CORS()
jwt = JWTManager()
mail = Mail()
sess = Session()


def start_extensions(app: Flask) -> None:
    """Inicializa as extensões do Flask."""
    with app.app_context():
        db.init_app(app)
        cors.init_app(app)
        jwt.init_app(app)
        mail.init_app(app)
