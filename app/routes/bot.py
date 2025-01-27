import json
import os
import pathlib
import platform
import traceback
from typing import Type

from celery import Task
from celery.schedules import crontab
from flask import Blueprint, Response
from flask import current_app as app
from flask import jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy

from miscellaneous import reload_module

from ..misc import GeoLoc, check_latest, stop_execution
from ..models import ScheduleModel

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.post("/bot/<id>/<system>/<typebot>")
def botlaunch(id: int, system: str, typebot: str) -> Response:

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

                if system == "esaj" and platform.system() != "Windows":
                    raise Exception("Este servidor não pode executar este robô!")

                elif system == "caixa" and loc != "Amazonas":
                    raise Exception("Este servidor não pode executar este robô!")

                start_rb = SetStatus(data_bot, request.files, id, system, typebot)
                path_args, display_name = start_rb.start_bot(app, db)

                with app.app_context():

                    reload_module("bot")

                    from app.models import ThreadBots
                    from bot import WorkerThread

                    bot_starter = WorkerThread.start_bot

                    pid = pathlib.Path(path_args).stem

                    init_bot: Task = bot_starter
                    task = init_bot.delay(path_args, display_name, system, typebot)

                    process_id = str(task.id)
                    # if not app.testing:  # pragma: no cover

                    # elif app.testing:

                    #     import random
                    #     import string

                    #     digits = random.sample(string.digits, 6)
                    #     process_id = "".join(digits)

                    # Salva o ID no "banco de dados"
                    add_thread = ThreadBots(pid=pid, processID=process_id)
                    db.session.add(add_thread)
                    db.session.commit()

            elif app.testing is True:
                is_started = 200 if data_bot else 500

        except Exception as e:  # pragma: no cover

            print(traceback.format_exc())
            message = {"error": str(e)}
            is_started: Type[int] = 500

    resp = make_response(jsonify(message), is_started)
    return resp


@bot.route("/stop/<user>/<pid>", methods=["POST"])
def stop_bot(user: str, pid: str) -> Response:  # pragma: no cover

    from flask import current_app as app

    from app.models import Executions

    db: SQLAlchemy = app.extensions["sqlalchemy"]
    query = db.session.query(Executions).filter(Executions.pid == pid).first()
    if query:
        pid = query.pid
        with app.app_context():
            args, code = stop_execution(app, pid, True)

            return make_response(jsonify(args), code)

    return make_response(jsonify({"error": "PID não encontrado"}), 404)


@bot.post("/periodic_bot/<id>/<system>/<typebot>")
def periodic_bot(id: int, system: str, typebot: str) -> Response:

    from status import SetStatus

    db: SQLAlchemy = app.extensions["sqlalchemy"]

    request_data = request.data
    request_form = request.form

    data_bot = request_data if request_data else request_form

    if isinstance(data_bot, str):  # pragma: no cover
        data_bot = json.loads(data_bot)

    # cron = crontab(
    #     minute="*/1", hour="*", day_of_month="*", month_of_year="*", day_of_week="*"
    # )

    cron = crontab(**data_bot.get("CRONTAB_ARGS"))

    start_rb = SetStatus(data_bot, request.files, id, system, typebot)
    path_args, display_name = start_rb.start_bot(app, db)

    schedule_str = f"{cron._orig_minute} {cron._orig_hour} {cron._orig_day_of_month} {cron._orig_month_of_year} {cron._orig_day_of_week}"

    task_name = "app.tasks.bot_starter.init_bot"
    args = json.dumps([path_args, display_name, system, typebot])
    kwargs = json.dumps({})

    new_schedule = ScheduleModel(
        task_name=task_name, schedule=schedule_str, args=args, kwargs=kwargs
    )
    db.session.add(new_schedule)
    db.session.commit()

    return make_response(jsonify({"success": "success"}))
