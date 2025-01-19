import importlib
import json
import os
import pathlib
import platform
import sys
from typing import Type

from celery import Task
from flask import Blueprint, Response, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy

from ..misc import GeoLoc, stop_execution
from ..misc.checkout import check_latest
from ..tasks import init_bot as bot_starter

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


def reload_module(module_name: str) -> None:  # pragma: no cover
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)


@bot.route("/bot/<id>/<system>/<typebot>", methods=["POST"])
def botlaunch(id: int, system: str, typebot: str) -> Response:

    from app import app, db

    message = {"success": "success"}
    from status import SetStatus

    reload_module("bot")

    is_started = 200

    with app.app_context():
        try:
            obj = GeoLoc()
            loc = obj.region_name

            request_data = request.data
            request_form = request.form

            data_bot = request_data if request_data else request_form

            if isinstance(data_bot, str):  # pragma: no cover
                data_bot = json.loads(data_bot)

            if check_latest() is False and app.debug is False:  # pragma: no cover
                raise Exception("Server running outdatest version!")

            if app.testing is False:  # pragma: no cover

                if system == "esaj" and platform.system() != "Windows":
                    raise Exception("Este servidor não pode executar este robô!")

                elif system == "caixa" and loc != "Amazonas":
                    raise Exception("Este servidor não pode executar este robô!")

                start_rb = SetStatus(data_bot, request.files, id, system, typebot)
                path_args, display_name = start_rb.start_bot(app, db)

                with app.app_context():

                    from app.models import ThreadBots

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
            print(e)
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


# @bot.route("/periodics_runs")
# def list_processos() -> Response:

#     from ..tasks import seach_intimacao

#     # celery: Celery = app.extensions["celery"]
#     result = seach_intimacao.delay("teste")

#     db: SQLAlchemy = app.extensions["sqlalchemy"]

#     kwargs = {}
#     cron = crontab(
#         minute="*/1", hour="*", day_of_month="*", month_of_year="*", day_of_week="*"
#     )
#     schedule_str = f"{cron._orig_minute} {cron._orig_hour} {cron._orig_day_of_month} {cron._orig_month_of_year} {cron._orig_day_of_week}"

#     task_name = "app.tasks.search_.seach_intimacao"
#     args = json.dumps(["teste"])
#     kwargs = json.dumps(kwargs)

#     new_schedule = ScheduleModel(
#         task_name=task_name, schedule=schedule_str, args=args, kwargs=kwargs
#     )
#     db.session.add(new_schedule)
#     db.session.commit()

#     return jsonify({"result": result.id})
