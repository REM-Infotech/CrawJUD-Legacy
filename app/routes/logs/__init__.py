from flask_socketio import emit, join_room, leave_room, send

from app import app, io
from app.misc import stop_execution
from status.server_side import load_cache, serverSide


@io.on("connect", namespace="/log")
def on_connect():
    send("connected!")


@io.on("disconnect", namespace="/log")
def on_disconnect():
    send("disconnected!")


@io.on("leave", namespace="/log")
def on_leave(data):
    room = data["pid"]
    leave_room(room)
    send(f"Leaving Room '{room}'")


@io.on("join", namespace="/log")
def on_join(data: dict[str, str]):

    room = data["pid"]
    join_room(room)

    data = load_cache(room, app)
    emit("log_message", data, room=room)
    send(f"Joinned room! Room: {room}")


@io.on("stop_bot", namespace="/log")
def on_stop_bot(data: dict[str, str]):

    pid = data["pid"]
    stop_execution(app, pid)
    send("Bot stopped!")


@io.on("terminate_bot", namespace="/log")
def on_terminate_bot(data: dict[str, str]):

    from app import db
    from app.models import ThreadBots
    from bot import WorkerThread

    try:
        pid = data["pid"]
        processID = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()

        if processID:
            processID = int(processID.processID)
            WorkerThread().stop(processID, pid, app)
            send("Bot stopped!")

    except Exception:
        send("Failed to stop bot!")


@io.on("log_message", namespace="/log")
def on_log_message(data: dict[str, str]):

    try:

        pid = data["pid"]

        if "message" in data:
            data = serverSide(data, pid, app)
            emit("log_message", data, room=pid)

        send("message received!")

    except Exception:
        send("failed to receive message")


@io.on("statusbot", namespace="/log")
def statusbot(data: dict):
    send("Bot stopped!")
