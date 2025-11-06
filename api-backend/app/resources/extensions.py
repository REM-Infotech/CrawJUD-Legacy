"""Extensões do App."""

from __future__ import annotations

from celery import Celery
from dynaconf.contrib import DynaconfConfig
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from socketio.redis_manager import RedisManager

from app.base import Model, Query
from app.resources._minio import Minio

celery = Celery(__name__)
db = SQLAlchemy(model_class=Model, query_class=Query)  # pyright: ignore[reportArgumentType]
jwt = JWTManager()
mail = Mail()
io = SocketIO()
cors = CORS()
storage = Minio()

__all__ = ["cors", "db", "jwt", "mail", "start_extensions"]


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
        storage.init_app(app)

        class CeleryConfig:
            def __init__(self, values: DynaconfConfig) -> None:
                for k, v in list(values.items()):
                    if str(k).isupper():
                        setattr(self, k, v)

        celery.config_from_object(CeleryConfig(app.config))
