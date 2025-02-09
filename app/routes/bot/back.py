"""Blueprint for managing bot operations such as launching, stopping, and scheduling."""

import asyncio
import json
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from celery.schedules import crontab
from quart import Response, jsonify, make_response, request
from quart import current_app as app

from utils import (  # noqa: F401
    check_latest,
    reload_module,  # noqa: F401
    stop_execution,
)

from ...models import ScheduleModel
from . import bot

if TYPE_CHECKING:
    from celery import Task
    from flask_sqlalchemy import SQLAlchemy


@bot.post("/bot/<id>/<system>/<typebot>")
async def botlaunch_back(id: int, system: str, typebot: str) -> Response:  # noqa: A002
    """Launch a new bot with the specified parameters.

    Args:
        id (int): The identifier for the bot.
        system (str): The system the bot is associated with.
        typebot (str): The type of bot to launch.

    Returns:
        Response: JSON response indicating the success or error of the launch operation.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    message = {"success": "success"}
    from utils import SetStatus

    is_started = 200

    async with app.app_context():
        try:
            # obj = GeoLoc()
            # loc = obj.region_name

            request_data = await request.data
            request_form = await request.form

            data_bot = request_data or request_form

            # Check if data_bot is enconded
            if isinstance(data_bot, bytes):
                data_bot = data_bot.decode("utf-8")

            if isinstance(data_bot, str):
                if "\\" in data_bot:
                    data_bot = data_bot.replace("\\", "")

                data_bot = json.loads(data_bot)
                if not isinstance(data_bot, dict):
                    raise ValueError("Invalid data_bot format")

            # if (system == "esaj" and platform.system() != "Windows") or (system == "caixa" and loc != "Amazonas"):
            #     raise Exception("Este servidor não pode executar este robô!")

            start_rb = SetStatus()

            files = await request.files

            start_rb = await asyncio.create_task(start_rb.config(data_bot, files, id, system, typebot))
            path_args, display_name = await asyncio.create_task(start_rb.start_bot(app, db))

            async with app.app_context():
                # reload_module("bot")

                from app.models import ThreadBots
                from bot import WorkerBot

                bot_starter = WorkerBot.start_bot

                pid = Path(path_args).stem

                init_bot: Task = bot_starter
                task = init_bot.apply_async(args=[path_args, display_name, system, typebot])

                process_id = str(task.id)

                # Salva o ID no "banco de dados"
                add_thread = ThreadBots(pid=pid, processID=process_id)
                db.session.add(add_thread)
                db.session.commit()

        except Exception:
            err = traceback.format_exc()
            app.logger.exception(err)
            message = {"error": err}
            is_started: type[int] = 500

    return await make_response(jsonify(message), is_started)


@bot.route("/stop/<user>/<pid>", methods=["POST"])
async def stop_bot(user: str, pid: str) -> Response:
    """Stop a running bot based on user and PID.

    Args:
        user (str): The user requesting the stop.
        pid (str): The PID of the bot to stop.

    Returns:
        Response: JSON response indicating the result of the stop operation.

    """
    from quart import current_app as app

    from app.models import Executions

    db: SQLAlchemy = app.extensions["sqlalchemy"]
    query = db.session.query(Executions).filter(Executions.pid == pid).first()
    if query:
        pid = query.pid
        with app.app_context():
            robot_stop = True
            args, code = stop_execution(app, pid, robot_stop)

            return await make_response(jsonify(args), code)

    return await make_response(jsonify({"error": "PID não encontrado"}), 404)


@bot.post("/periodic_bot/<id>/<system>/<typebot>")
async def periodic_bot(id: int, system: str, typebot: str) -> Response:  # noqa: A002
    """Schedule a bot to run periodically based on provided cron arguments.

    Args:
        id (int): The identifier for the bot.
        system (str): The system the bot is associated with.
        typebot (str): The type of bot to schedule.

    Returns:
        Response: JSON response indicating the success of the scheduling operation.

    """
    from utils import SetStatus

    db: SQLAlchemy = app.extensions["sqlalchemy"]

    request_data = request.data
    request_form = request.form

    data_bot = request_data or request_form

    if isinstance(data_bot, str):
        data_bot = json.loads(data_bot)

    cron = crontab(minute="*/1", hour="*", day_of_month="*", month_of_year="*", day_of_week="*")

    cron = crontab(**data_bot.get("CRONTAB_ARGS"))

    start_rb = SetStatus(data_bot, request.files, id, system, typebot)
    path_args, display_name = start_rb.start_bot(app, db)

    schedule_str = "".join(
        (
            f"{cron._orig_minute} {cron._orig_hour} {cron._orig_day_of_month}",  # noqa: SLF001
            f"{cron._orig_month_of_year} {cron._orig_day_of_week}",  # noqa: SLF001
        ),
    )

    task_name = "app.tasks.bot_starter.init_bot"
    args = json.dumps([path_args, display_name, system, typebot])
    kwargs = json.dumps({})

    new_schedule = ScheduleModel(task_name=task_name, schedule=schedule_str, args=args, kwargs=kwargs)
    db.session.add(new_schedule)
    db.session.commit()

    return await make_response(jsonify({"success": "success"}))
