"""Log bot."""

from __types import MyAny
from _interfaces import Message
from flask_socketio import join_room
from tqdm import tqdm

from app.resources.extensions import io


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
    io.emit("logbot", data=data, room=data["pid"], namespace="/bot_logs")
