"""Socket.IO event handlers for logging and managing bot executions."""

import asyncio
import logging
import traceback
from datetime import datetime

from pytz import timezone
from socketio import AsyncServer

from app import app
from utils import format_message_log, load_cache
from utils.status import TaskExec

logger = logging.getLogger(__name__)

io: AsyncServer = app.extensions["socketio"]


@io.on("connect", namespace="/log")
async def connect(sid: str = None, data: dict = None) -> None:
    """Handle a new client connection to the /log namespace.

    Args:
        sid: The session ID of the client.
        data: Data sent by the client.

    """
    room = data.get("HTTP_PID", None)

    if room:
        await io.enter_room(sid, room, namespace="/log")

    await io.send("connected!", to=sid, namespace="/log")


@io.on("disconnect", namespace="/log")
async def disconnect(
    sid: str = None,
    event: any = None,
    namespace: str = None,
) -> None:
    """Handle client disconnection from the /log namespace."""
    await io.send("disconnected!", to=sid, namespace="/log")


@io.on("leave", namespace="/log")
async def leave(sid: str, data: dict) -> None:  # noqa: ARG001, RUF100
    """Handle a client leaving a specific logging room.

    Args:
        sid: The session ID of the client.
        data: Data containing the room identifier (pid).

    """
    room = data["pid"]
    await io.send(f"Leaving Room '{room}'", to=sid, namespace="/log")
    await io.leave_room(sid, room, "/log")


@io.on("stop_bot", namespace="/log")
async def stop_bot(sid: str, data: dict[str, str]) -> None:
    """Stop a running bot identified by its PID.

    Args:
        data (dict[str, str]): Data containing the PID of the bot to stop.
        sid (str): The session ID of the client.

    """
    pid = data["pid"]
    await TaskExec.task_exec(data_bot=data, exec_type="stop", app=app)
    await io.send({"message": "Bot stopped!"}, to=sid, namespace="/log", room=pid)


@io.on("terminate_bot", namespace="/log")
async def terminate_bot(sid: str, data: dict[str, str]) -> None:
    """Terminate a running bot identified by its PID.

    Args:
        data (dict[str, str]): Data containing the PID of the bot to terminate.
        sid (str): The session ID of the client.

    """
    from app import db
    from app.models import ThreadBots
    from bot import WorkerBot

    async with app.app_context():
        try:
            pid = data["pid"]
            process_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()  # noqa: N806
            if process_id:
                process_id = str(process_id.processID)  # noqa: N806

            result = await asyncio.create_task(WorkerBot.stop(process_id, pid, app))
            await io.enter_room(sid, pid, namespace="/log")
            await io.emit("log_message", result, to=sid, namespace="/log", room=pid)

        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            await io.send("Failed to stop bot!", to=sid, namespace="/log", room=pid)


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
                data = await format_message_log(data, pid, app)

                await io.emit("log_message", data, room=pid, namespace="/log")

            await io.send("message received!", to=sid, namespace="/log", room=pid)

        except Exception:
            err = traceback.format_exc()
            logger.exception(err)
            await io.send("failed to receive message", to=sid, namespace="/log", room=pid)


@io.on("statusbot", namespace="/log")
async def statusbot(sid: str, data: dict = None) -> None:
    """Handle status updates from bots.

    Args:
        sid (str): The session ID of the client.
        data (dict): Data containing status information.
        sid (str): The session ID of the client.

    """
    if data:
        room = data.get("pid", None)
        await io.send("Bot stopped!", to=sid, namespace="/log", room=room)

    await io.send("Bot stopped!", to=sid, namespace="/log")


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

    async with app.app_context():
        try:
            data = await load_cache(room, app)
            from app import db
            from app.models import ThreadBots
            from bot import WorkerBot

            pid = room
            process_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()

            message = "Fim da Execução"

            if process_id:
                process_id = process_id.processID

            message = await WorkerBot.check_status(process_id, pid, app)

            if message != "Process running!":
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

                # try:
                #     await stop_execution(app, pid)
                # except Exception as e:
                #     app.logger.error("An error occurred: %s", str(e))
                #     app.logger.exception(traceback.format_exc())
            data = await format_message_log(data, pid, app)
            await io.emit("log_message", data, room=room, namespace="/log")

        except Exception:
            await io.send("Failed to check bot has stopped")
            # stop_execution(app, pid)

    await io.send(f"Joinned room! Room: {room}", to=sid, namespace="/log")
