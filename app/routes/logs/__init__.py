from flask import abort
from flask_socketio import emit, join_room, leave_room, send

from app import app, io
from app.misc import stop_execution
from status.server_side import load_cache, serverSide


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

    data = load_cache(room, app)
    emit("log_message", data, room=room)
    # if StatusStop(room) is True:
    #     emit("statusbot", data=data)

    # elif stopped_bot(room) is True:
    #     stop_execution(app, room, True)


@io.on("stop_bot", namespace="/log")
def on_stop_bot(data: dict[str, str]):

    pid = data["pid"]
    stop_execution(app, pid)


@io.on("terminate_bot", namespace="/log")
def on_terminate_bot(data: dict[str, str]):

    from app import db
    from app.models import ThreadBots
    from bot import WorkerThread

    pid = data["pid"]

    try:

        processID = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()

        if processID:
            processID = int(processID.processID)
            WorkerThread().stop(processID, pid, app)

    except Exception as e:
        print(e)


@io.on("log_message", namespace="/log")
def on_log_message(data: dict[str, str]):

    try:

        if data:
            pid = data["pid"]
            data = serverSide(data, pid, app)
            emit("log_message", data, room=pid)

    except Exception as e:
        abort(500, description=str(e))


@io.on("statusbot", namespace="/log")
def statusbot(data: dict):
    send("Bot stopped!")
