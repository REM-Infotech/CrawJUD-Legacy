"""WebSocket event handlers for logging and managing bot executions."""

import traceback
from datetime import datetime
from typing import NoReturn

from pytz import timezone
from quart import websocket

from app import app
from app.misc import stop_execution
from status.server_side import FormatMessage, load_cache


@app.websocket("/log")
async def log() -> NoReturn:
    """Handle WebSocket events for logging and managing bot executions."""
    while True:
        data = await websocket.receive_json()
        event = data.get("event")
        if event == "connect":
            await connect()
        elif event == "disconnect":
            await disconnect()
        elif event == "leave":
            await leave(data)
        elif event == "stop_bot":
            await stop_bot(data)
        elif event == "terminate_bot":
            await terminate_bot(data)
        elif event == "log_message":
            await log_message(data)
        elif event == "statusbot":
            await statusbot(data)
        elif event == "join":
            await join(data)


async def connect() -> None:
    """Handle a new client connection to the /log namespace."""
    await websocket.send_json({"message": "connected!"})


async def disconnect() -> None:
    """Handle client disconnection from the /log namespace."""
    await websocket.send_json({"message": "disconnected!"})


async def leave(data: dict) -> None:
    """Handle a client leaving a specific logging room.

    Args:
        data (dict): Data containing the room identifier (pid).

    """
    room = data["pid"]
    await websocket.send_json({"message": f"Leaving Room '{room}'"})


async def stop_bot(data: dict[str, str]) -> None:
    """Stop a running bot identified by its PID.

    Args:
        data (dict[str, str]): Data containing the PID of the bot to stop.

    """
    pid = data["pid"]
    stop_execution(app, pid)
    await websocket.send_json({"message": "Bot stopped!"})


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
            await websocket.send_json({"message": "Bot stopped!"})

    except Exception:
        await websocket.send_json({"message": "Failed to stop bot!"})


async def log_message(data: dict[str, str]) -> None:
    """Handle incoming log messages from bots.

    Args:
        data (dict[str, str]): Data containing the log message and PID.

    """
    try:
        pid = data["pid"]

        if "message" in data:
            data = FormatMessage(data, pid, app)
            await websocket.send_json({"event": "log_message", "data": data})

        await websocket.send_json({"message": "message received!"})

    except Exception:
        err = traceback.format_exc()
        app.logger.exception(err)
        await websocket.send_json({"message": "failed to receive message"})


async def statusbot(data: dict) -> None:
    """Handle status updates from bots.

    Args:
        data (dict): Data containing status information.

    """
    await websocket.send_json({"message": "Bot stopped!"})


async def join(data: dict[str, str]) -> None:
    """Handle a client joining a specific logging room.

    Args:
        data (dict[str, str]): Data containing the room identifier (pid).

    """
    room = data["pid"]
    data = load_cache(room, app)

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

            if message == f"Process {processID} stopped!":
                stop_execution(app, pid)
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
                await websocket.send_json({"event": "log_message", "data": data})

            elif message == "Erro ao inicializar robô":
                stop_execution(app, pid)
                await websocket.send_json({"event": "log_message", "data": data})

    except Exception:
        await websocket.send_json({"message": "Failed to check bot has stopped"})
        stop_execution(app, pid)

    await websocket.send_json({"message": f"Joined room! Room: {room}"})
