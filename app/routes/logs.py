"""Socket.IO event handlers for logging and managing bot executions."""

import logging
import traceback
from datetime import datetime

from pytz import timezone

from app import app, io
from utils import FormatMessage, load_cache, stop_execution

logger = logging.getLogger(__name__)


@io.on("connect", namespace="/log")
async def connect(sid: str = None, event: any = None, namespace: str = None) -> None:
    """Handle a new client connection to the /log namespace.

    Args:
        sid: The session ID of the client.
        event: The event that triggered the connection.
        namespace: The namespace the client is connecting

    """
    await io.send("connected!")


@io.on("disconnect", namespace="/log")
async def disconnect(
    sid: str = None,
    event: any = None,
    namespace: str = None,
) -> None:
    """Handle client disconnection from the /log namespace."""
    await io.send("disconnected!")


@io.on("leave", namespace="/log")
async def leave(sid: str, data: dict) -> None:  # noqa: ARG001, RUF100
    """Handle a client leaving a specific logging room.

    Args:
        sid: The session ID of the client.
        data: Data containing the room identifier (pid).

    """
    room = data["pid"]
    await io.leave_room(sid, room)
    await io.send(f"Leaving Room '{room}'")


@io.on("stop_bot", namespace="/log")
async def stop_bot(data: dict[str, str]) -> None:
    """Stop a running bot identified by its PID.

    Args:
        data (dict[str, str]): Data containing the PID of the bot to stop.

    """
    pid = data["pid"]
    stop_execution(app, pid)
    io.send("Bot stopped!")


@io.on("terminate_bot", namespace="/log")
async def terminate_bot(data: dict[str, str]) -> None:
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
            io.send("Bot stopped!")

    except Exception:
        io.send("Failed to stop bot!")


@io.on("log_message", namespace="/log")
async def log_message(sid: str, data: dict[str, str] = None) -> None:
    """Handle incoming log messages from bots.

    Args:
        sid (str): The session ID of the client.
        data (dict[str, str]): Data containing the log message and PID.

    """
    async with app.app_context():
        try:
            pid = data["pid"]

            if "message" in data:
                data = FormatMessage(data, pid, app)

                await io.emit("log_message", data, room=pid, namespace="/log")

            await io.send("message received!", namespace="/log")

        except Exception:
            err = traceback.format_exc()
            logger.exception(err)
            io.send("failed to receive message", namespace="/log")


@io.on("statusbot", namespace="/log")
async def statusbot(sid: str, data: dict = None) -> None:
    """Handle status updates from bots.

    Args:
        sid (str): The session ID of the client.
        data (dict): Data containing status information.

    """
    if data:
        room = data.get("pid", None)

    await io.send("Bot stopped!", namespace="/log", room=room)


@io.on("join", namespace="/log")
async def join(
    sid: str = None,
    data: dict[str, str] = None,
    namespace: str = None,
) -> None:
    """Handle a client joining a specific logging room.

    Args:
        data (dict[str, str]): Data containing the room identifier (pid).
        event (any): The event that triggered the join.
        sid (str): The session ID of the client.
        namespace (str): The namespace the client is joining.

    """
    room = data["pid"]
    await io.enter_room(sid, room, namespace="/log")
    data = load_cache(room, app)
    async with app.app_context():
        try:
            from app import db
            from app.models import ThreadBots
            from bot import WorkerBot

            pid = room
            processID = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()  # noqa: N806

            message = "Fim da Execução"

            if processID:
                processID = processID.processID  # noqa: N806

            message = WorkerBot.check_status(processID)

            if message == f"Process {processID} stopped!" or message == "Process stopped!":
                try:
                    stop_execution(app, pid)
                except Exception:
                    app.logger.error(traceback.format_exc())

                data.update(
                    {
                        "message": "[({pid}, {type_log}, {row}, {dateTime})> {log}]".format(
                            pid=pid,
                            type_log="success",
                            row=0,
                            dateTime=datetime.now(timezone("America/Manaus")).strftime("%H:%M:%S"),
                            log="fim da execução",
                        ),
                    },
                )
                await io.emit("log_message", data, room=room, namespace="/log")

            elif message == "Erro ao inicializar robô":
                stop_execution(app, pid)

            else:
                await io.emit("log_message", data, room=room, namespace="/log")

        except Exception:
            await io.send("Failed to check bot has stopped")
            stop_execution(app, pid)

    await io.send(f"Joinned room! Room: {room}", namespace="/log")
