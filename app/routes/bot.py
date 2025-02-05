"""Blueprint for managing bot operations such as launching, stopping, and scheduling."""

import json
import pathlib
import platform
import traceback
from typing import TYPE_CHECKING

from celery.schedules import crontab
from flask import Blueprint, Response, jsonify, make_response, request
from flask import current_app as app

from miscellaneous import reload_module

from ..misc import check_latest, stop_execution
from ..models import ScheduleModel
from ..utils import GeoLoc

if TYPE_CHECKING:
    from celery import Task
    from flask_sqlalchemy import SQLAlchemy

path_template = str(pathlib.Path(__file__).parent.resolve().joinpath("templates"))
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.post("/bot/<id>/<system>/<typebot>")
def botlaunch(id: int, system: str, typebot: str) -> Response:  # noqa: A002
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
    from status import SetStatus

    is_started = 200

    with app.app_context():
        try:
            obj = GeoLoc()
            loc = obj.region_name

            request_data = request.data
            request_form = request.form

            data_bot = request_data if request_data else request_form

            if isinstance(data_bot, str):
                data_bot = json.loads(data_bot)

            if check_latest() is False and app.debug is False:
                raise Exception("Server running outdatest version!")

            if app.testing is False:
                if (system == "esaj" and platform.system() != "Windows") or (system == "caixa" and loc != "Amazonas"):
                    raise Exception("Este servidor não pode executar este robô!")

                start_rb = SetStatus(data_bot, request.files, id, system, typebot)
                path_args, display_name = start_rb.start_bot(app, db)

                with app.app_context():
                    reload_module("bot")

                    from app.models import ThreadBots
                    from bot import WorkerBot

                    bot_starter = WorkerBot.start_bot

                    pid = pathlib.Path(path_args).stem

                    init_bot: Task = bot_starter
                    task = init_bot.delay(path_args, display_name, system, typebot)

                    process_id = str(task.id)

                    # Salva o ID no "banco de dados"
                    add_thread = ThreadBots(pid=pid, processID=process_id)
                    db.session.add(add_thread)
                    db.session.commit()

            elif app.testing is True:
                is_started = 200 if data_bot else 500

        except Exception:
            err = traceback.format_exc()
            app.logger.exception(err)
            message = {"error": err}
            is_started: type[int] = 500

    resp = make_response(jsonify(message), is_started)
    return resp


@bot.route("/stop/<user>/<pid>", methods=["POST"])
def stop_bot(user: str, pid: str) -> Response:
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
def periodic_bot(id: int, system: str, typebot: str) -> Response:  # noqa: A002
    """Schedule a bot to run periodically based on provided cron arguments.

    Args:
        id (int): The identifier for the bot.
        system (str): The system the bot is associated with.
        typebot (str): The type of bot to schedule.

    Returns:
        Response: JSON response indicating the success of the scheduling operation.

    """
    from status import SetStatus

    db: SQLAlchemy = app.extensions["sqlalchemy"]

    request_data = request.data
    request_form = request.form

    data_bot = request_data if request_data else request_form

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
