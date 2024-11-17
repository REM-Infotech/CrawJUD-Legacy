from flask import Blueprint, request, jsonify, make_response

import os

import json
import pathlib
import platform

from bot import WorkerThread
from ..misc import GeoLoc, stop_execution
from ..misc.checkout import check_latest

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.route("/bot/<id>/<system>/<typebot>", methods=["POST"])
def botlaunch(id: int, system: str, typebot: str):

    from app import app, db

    message = {"success": "success"}
    from status import SetStatus

    with app.app_context():
        try:

            if check_latest() is False:
                raise Exception("Server running outdatest version!")

            loc = GeoLoc().region_name
            if request.data:
                data_bot = json.loads(request.data)

            elif request.form:
                data_bot = request.form

            if isinstance(data_bot, str):
                data_bot = json.loads(data_bot)

            if system == "esaj" and platform.system() != "Windows":
                raise Exception("Este servidor não pode executar este robô!")

            elif system == "caixa" and loc != "Amazonas":
                raise Exception("Este servidor não pode executar este robô!")

            start_rb = SetStatus(data_bot, request.files, id, system, typebot)
            path_args, display_name = start_rb.start_bot()
            worker_thread = WorkerThread(
                path_args=path_args,
                display_name=display_name,
                system=system,
                typebot=typebot,
            )
            is_started = worker_thread.start(app, db)

        except Exception as e:
            message = {"error": str(e)}
            is_started = 500

    resp = make_response(jsonify(message), is_started)
    return resp


@bot.route("/stop/<user>/<pid>", methods=["POST"])
def stop_bot(user: str, pid: str):

    from app import app

    with app.app_context():
        set_stop = stop_execution(app, pid, True)

        if set_stop == 200:

            return jsonify({"Encerrado!": "Sucesso"}), set_stop

        elif set_stop != 200:
            return jsonify({"mensagem": "erro"}), set_stop
