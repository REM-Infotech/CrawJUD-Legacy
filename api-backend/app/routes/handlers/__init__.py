"""Log bot."""

from pathlib import Path

from __types import MyAny
from _interfaces import Message
from flask import request
from flask_socketio import join_room
from tqdm import tqdm
from werkzeug.utils import secure_filename

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


@io.on("add_file", namespace="/files")
def add_file(data: MyAny) -> None:
    """Log bot."""
    sid = request.sid
    path_file = Path.cwd().joinpath(
        "output", sid, secure_filename(data["name"])
    )
    path_file.parent.mkdir(exist_ok=True, parents=True)

    mode = "ab"
    if not path_file.exists():
        mode = "wb"

    with path_file.open(mode=mode) as fp:
        fp.write(data["chunk"])
