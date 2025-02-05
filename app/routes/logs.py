"""Socket.IO event handlers for logging and managing bot executions."""

import logging
import traceback
from datetime import datetime

from flask_socketio import emit, join_room, leave_room, send
from pytz import timezone

from app import app, io
from app.misc import stop_execution
from status.server_side import FormatMessage  # load_cache, FormatMessage


@io.on("connect", namespace="/log")
def connect() -> None:
    """Handle a new client connection to the /log namespace."""
    send("connected!")


@io.on("disconnect", namespace="/log")
def disconnect() -> None:
    """Handle client disconnection from the /log namespace."""
    send("disconnected!")


@io.on("leave", namespace="/log")
def leave(data) -> None:
    """Handle a client leaving a specific logging room.

    Args:
        data: Data containing the room identifier (pid).

    """
    room = data["pid"]
    leave_room(room)
    send(f"Leaving Room '{room}'")


@io.on("stop_bot", namespace="/log")
def stop_bot(data: dict[str, str]) -> None:
    """Stop a running bot identified by its PID.

    Args:
        data (dict[str, str]): Data containing the PID of the bot to stop.

    """
    pid = data["pid"]
    stop_execution(app, pid)
    send("Bot stopped!")


@io.on("terminate_bot", namespace="/log")
def terminate_bot(data: dict[str, str]) -> None:
    """Terminate a running bot identified by its PID.

    Args:
        data (dict[str, str]): Data containing the PID of the bot to terminate.

    """
    from app import db
    from app.models import ThreadBots
    from bot import WorkerBot

    try:
        pid = data["pid"]
        processID = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()  # noqa: N806

        if processID:
            processID = str(processID.processID)  # noqa: N806
            WorkerBot.stop(processID, pid, app)
            send("Bot stopped!")

    except Exception:
        send("Failed to stop bot!")


@io.on("log_message", namespace="/log")
def log_message(data: dict[str, str]) -> None:
    """Handle incoming log messages from bots.

    Args:
        data (dict[str, str]): Data containing the log message and PID.

    """
    try:
        pid = data["pid"]

        if "message" in data:
            data = FormatMessage(data, pid, app)
            emit("log_message", data, room=pid)

        send("message received!")

    except Exception:
        err = traceback.format_exc()
        logging.exception(err)
        send("failed to receive message")


@io.on("statusbot", namespace="/log")
def statusbot(data: dict) -> None:
    """Handle status updates from bots.

    Args:
        data (dict): Data containing status information.

    """
    send("Bot stopped!")


@io.on("join", namespace="/log")
def join(data: dict[str, str]) -> None:
    """Handle a client joining a specific logging room.

    Args:
        data (dict[str, str]): Data containing the room identifier (pid).

    """
    room = data["pid"]
    join_room(room)

    # data = load_cache(room, app)
    try:  # pragma: no cover
        from app import db
        from app.models import ThreadBots
        from bot import WorkerBot

        pid = room
        processID = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()  # noqa: N806

        message = "Fim da Execução"

        if processID:
            processID = processID.processID  # noqa: N806
            message = WorkerBot.check_status(processID)

            if message == f"Process {processID} stopped!":
                stop_execution(app, pid)
                data.update(
                    {
                        "message": "[({pid}, {type_log}, {row}, {dateTime})> {log}]".format(
                            pid=pid, type_log="success", row=0, dateTime=datetime.now(timezone("America/Manaus")).strftime("%H:%M:%S"), log="fim da execução"
                        )
                    }
                )
            elif message == "Erro ao inicializar robô":
                # data = FormatMessage(
                #     {"type": "error", "pid": room, "message": message}, room, app
                # )
                stop_execution(app, pid)

    except Exception:
        send("Failed to check bot has stopped")
        # data = FormatMessage(
        #     {"type": "error", "pid": room, "message": message}, room, app
        # )
        stop_execution(app, pid)

    emit("log_message", data, room=room)
    send(f"Joinned room! Room: {room}")
