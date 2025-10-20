"""Extensões do App."""

from __future__ import annotations

from typing import Literal

from __types import MyAny
from _interfaces import Message
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO, join_room
from flask_sqlalchemy import SQLAlchemy
from tqdm import tqdm

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


def cors_origin(*args, **kwargs) -> Literal[True]:
    return True


io = SocketIO(
    async_mode="threading",
    cors_allowed_origins="*",
)


@io.on("connect", namespace="/bot_logs")
def connected(*args: MyAny, **kwargs: MyAny) -> None:
    """Log bot."""


@io.on("join_room", namespace="/bot_logs")
def join_room_bot(data: dict[str, str]) -> None:
    """Log bot."""
    join_room(data["room"])


@io.on("logbot", namespace="/bot_logs")
def log_bot(data: Message) -> None:
    """Log bot."""
    tqdm.write(data["message"])


__all__ = ["db", "cors", "jwt", "mail", "start_extensions"]


def start_extensions(app: Flask) -> None:
    """Inicializa as extensões do Flask."""
    with app.app_context():
        db.init_app(app)
        cors.init_app(app)
        jwt.init_app(app)
        mail.init_app(app)
        io.init_app(app)
