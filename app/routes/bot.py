import importlib
import json
import os
import pathlib
import platform
import sys

from flask import Blueprint, jsonify, make_response, request

from bot import WorkerThread

from ..misc import GeoLoc, stop_execution
from ..misc.checkout import check_latest

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


def reload_module(module_name: str):  # pragma: no cover
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)


@bot.route("/bot/<id>/<system>/<typebot>", methods=["POST"])
def botlaunch(id: int, system: str, typebot: str):

    from app import app, db

    message = {"success": "success"}
    from status import SetStatus

    reload_module("bot")

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
                worker_thread = WorkerThread(
                    path_args=path_args,
                    display_name=display_name,
                    system=system,
                    typebot=typebot,
                )
                is_started = worker_thread.start(app, db)

            elif app.testing is True:
                is_started = 200 if data_bot else 500

        except Exception as e:  # pragma: no cover
            message = {"error": str(e)}
            is_started = 500

    resp = make_response(jsonify(message), is_started)
    return resp


@bot.route("/stop/<user>/<pid>", methods=["POST"])
def stop_bot(user: str, pid: str):

    from flask import current_app as app

    with app.app_context():
        args, code = stop_execution(app, pid, True)

        return jsonify(args), code
