"""Blueprint for managing bot operations such as launching, stopping, and scheduling."""

import json
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from quart import Blueprint, Response, jsonify, make_response, request
from quart import current_app as app

from utils import (  # noqa: F401
    check_latest,
    reload_module,
)
from utils.status import TaskExec

if TYPE_CHECKING:
    from celery import Celery
    from flask_sqlalchemy import SQLAlchemy

path_template = str(Path(__file__).parent.resolve().joinpath("templates"))
bot = Blueprint("bot", __name__, template_folder=path_template)


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
            request_json = await request.json

            data_bot = (request_json if isinstance(request_data, bytes) else request_data) or request_form

            # Check if data_bot is enconded
            if isinstance(data_bot, bytes):
                data_bot = data_bot.decode("utf-8")

            if isinstance(data_bot, str):
                if "\\" in data_bot:
                    data_bot = data_bot.replace("\\", "")

                if "'" in data_bot:
                    data_bot = data_bot.replace("'", "")

                data_bot = json.loads(data_bot)
                if not isinstance(data_bot, dict):
                    raise ValueError("Invalid data_bot format")

            # if (system == "esaj" and platform.system() != "Windows") or (system == "caixa" and loc != "Amazonas"):
            #     raise Exception("Este servidor não pode executar este robô!")

            files = await request.files
            celery_app: Celery = app.extensions["celery"]
            is_started = await TaskExec.task_exec(
                id_,
                system,
                typebot,
                "start",
                app,
                db,
                files,
                celery_app,
                data_bot,
            )

        except Exception:
            err = traceback.format_exc()
            app.logger.exception(err)
            message = {"error": err}
            is_started: type[int] = 500

    return await make_response(jsonify(message), is_started)


@bot.post("/periodic_bot/<id_>/<system>/<typebot>")
async def periodic_bot(id_: int, system: str, typebot: str) -> Response:
    """Schedule a bot to run periodically based on provided cron arguments.

    Args:
        id_ (int): The identifier for the bot.
        system (str): The system the bot is associated with.
        typebot (str): The type of bot to schedule.

    Returns:
        Response: JSON response indicating the success of the scheduling operation.

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
            request_json = bytes(await request.json, "utf-8").decode("unicode_escape")
            data_bot = (request_json if isinstance(request_data, bytes) else request_data) or request_form

            data_bot: dict[str, str, int, list[str]]

            # Check if data_bot is enconded
            if isinstance(data_bot, bytes):
                data_bot = data_bot.decode("utf-8")

            if isinstance(data_bot, str):
                if "\\" in data_bot:
                    data_bot = data_bot.replace("\\", "")

                if "'" in data_bot:
                    data_bot = data_bot.replace("'", "")

                data_bot = json.loads(data_bot)
                if not isinstance(data_bot, dict):
                    raise ValueError("Invalid data_bot format")

            files = await request.files

            is_started = await TaskExec.task_exec_schedule(
                id_,
                system,
                typebot,
                "start",
                app,
                db,
                files,
                data_bot,
            )

        except Exception:
            err = traceback.format_exc()
            app.logger.exception(err)
            message = {"error": err}
            is_started: type[int] = 500

    return await make_response(jsonify(message), is_started)
