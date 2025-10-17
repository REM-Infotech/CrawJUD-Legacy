from flask_socketio import join_room
from tqdm import tqdm

from app._types import MyAny
from app.resources.extensions import io


@io.on("connect", namespace="/bot_logs")
def connected(*args: MyAny, **kwargs: MyAny) -> None:
    tqdm.write("ok")


@io.on("join_room", namespace="/bot_logs")
def join_room_bot(*args: MyAny, **kwargs: MyAny) -> None:
    tqdm.write("ok")
    join_room()


@io.on("log_bot", namespace="/bot_logs")
def log_bot(*args: MyAny, **kwargs: MyAny) -> None:
    tqdm.write("ok")
