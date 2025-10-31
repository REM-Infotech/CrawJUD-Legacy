"""Log bot."""

from contextlib import suppress
from pathlib import Path

from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_socketio import join_room
from tqdm import tqdm
from werkzeug.utils import secure_filename

from __types import MyAny
from _interfaces import Message
from app.resources.extensions import io, storage


@io.on("connect", namespace="/")
@jwt_required()
def connected(*args: MyAny, **kwargs: MyAny) -> None:
    """Log bot."""
    tqdm.write("ok")


@io.on("join_room", namespace="/bot_logs")
def join_room_bot(data: dict[str, str]) -> None:
    """Log bot."""
    join_room(data["room"])


@io.on("logbot", namespace="/bot_logs")
@jwt_required()
def log_bot(data: Message) -> None:
    """Log bot."""
    tqdm.write(data["message"])
    io.emit(
        "logbot", data=data, room=data["pid"], namespace="/bot_logs"
    )


@io.on("add_file", namespace="/files")
@jwt_required()
def add_file(data: MyAny = None) -> None:
    """Log bot."""
    if data:
        bucket_name = current_app.config["MINIO_BUCKET_NAME"]
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

        with suppress(Exception):
            if path_file.stat().st_size >= data["fileSize"]:
                with path_file.open("rb") as fp:
                    storage.put_object(
                        bucket_name,
                        f"{sid}/{data['name']}",
                        data=fp,
                        length=path_file.stat().st_size,
                    )
                path_file.unlink()
                path_file.parent.rmdir()
