"""Blueprint for managing bot operations such as launching, stopping, and scheduling."""

import json
import traceback
from typing import TYPE_CHECKING

from celery.schedules import crontab
from quart import Response, jsonify, make_response, request
from quart import current_app as app

from utils import (  # noqa: F401
    SetStatus,
    check_latest,
    reload_module,  # noqa: F401
    stop_execution,
)

from ...models import ScheduleModel
from . import bot
from .task_exec import TaskExec

if TYPE_CHECKING:
    from celery import Celery
    from flask_sqlalchemy import SQLAlchemy


@bot.post("/bot/<id_>/<system>/<typebot>")
async def botlaunch(id_: int, system: str, typebot: str) -> Response:
    """Launch a new bot with the specified parameters.

    Args:
        id_ (int): The identifier for the bot.
        system (str): The system the bot is associated with.
        typebot (str): The type of bot to launch.

    Returns:
        Response: JSON response indicating the success or error of the launch operation.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    message = {"success": "success"}

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

            files = await request.files
            celery_app: Celery = app.extensions["celery"]
            await TaskExec.task_exec(app, celery_app, db, files, data_bot, id_, system, typebot)

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
    from flask import current_app as app

    from app.models import Executions

    db: SQLAlchemy = app.extensions["sqlalchemy"]
    query = db.session.query(Executions).filter(Executions.pid == pid).first()
    if query:
        pid = query.pid
        with app.app_context():
            robot_stop = True
            args, code = stop_execution(app, pid, robot_stop)

            return make_response(jsonify(args), code)

    return make_response(jsonify({"error": "PID não encontrado"}), 404)


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

    return make_response(jsonify({"success": "success"}))
