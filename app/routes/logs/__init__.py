from app import app, io
from flask import abort
from flask_socketio import emit, join_room, leave_room

from app.misc import stop_execution
from status.server_side import serverSide


@io.on("connect", namespace="/log")
def on_connect():
    emit("connected!")


@io.on("disconnect", namespace="/log")
def on_disconnect():
    emit("disconnected!")


@io.on("leave", namespace="/log")
def on_leave(data):
    room = data["pid"]
    leave_room(room)


@io.on("join", namespace="/log")
def on_join(data: dict[str, str]):

    room = data["pid"]
    join_room(room)

    # if StatusStop(room) is True:
    #     emit("statusbot", data=data)

    # elif stopped_bot(room) is True:
    #     stop_execution(app, room, True)


@io.on("stop_bot", namespace="/log")
def on_stop_bot(data: dict[str, str]):

    pid = data["pid"]
    stop_execution(app, pid, True)
    emit("statusbot", data=data)


@io.on("log_message", namespace="/log")
def on_log_message(data: dict[str, str]):

    try:
        pid = data["pid"]
        data = serverSide(data, pid)
        emit("log_message", data, room=pid)

    except Exception as e:
        abort(500, description=str(e))
