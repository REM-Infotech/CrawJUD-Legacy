"""Extensões do App."""

from __future__ import annotations

from celery import Celery
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from socketio.redis_manager import RedisManager

from app.base import Model, Query
from app.settings import settings

celery = Celery(__name__)
db = SQLAlchemy(model_class=Model, query_class=Query)  # pyright: ignore[reportArgumentType]
jwt = JWTManager()
mail = Mail()
io = SocketIO()
cors = CORS()


__all__ = ["db", "cors", "jwt", "mail", "start_extensions"]


def start_extensions(app: Flask) -> None:
    """Inicializa as extensões do Flask."""
    with app.app_context():
        db.init_app(app)
        jwt.init_app(app)
        mail.init_app(app)
        io.init_app(
            app,
            json=app.json,
            async_mode="threading",
            cors_allowed_origins="*",
            client_manager=RedisManager(app.config["BROKER_URL"]),
        )
        cors.init_app(
            app,
            allow_headers=["Content-Type", "Authorization"],
            supports_credentials=True,
            transports=["websocket"],
        )

        celery.config_from_object(settings)
