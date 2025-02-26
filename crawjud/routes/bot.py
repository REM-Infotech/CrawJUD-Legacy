"""Module for managing bot operations.

This module defines endpoints for launching bots, stopping them, and scheduling periodic bot tasks.
All endpoints process incoming request data, perform necessary validations, and invoke TaskExec methods.
"""

import json  # Handle JSON serialization/deserialization.
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from quart import Blueprint, Response, jsonify, make_response, request
from quart import current_app as app

from crawjud.utils import check_latest, reload_module  # noqa: F401
from crawjud.utils.status import TaskExec

if TYPE_CHECKING:
    from celery import Celery
    from flask_sqlalchemy import SQLAlchemy

# Define the path for template files relative to this module.
path_template = str(Path(__file__).parent.resolve().joinpath("templates"))
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.post("/bot/<id_>/<system>/<typebot>")
async def botlaunch(id_: int, system: str, typebot: str) -> Response:
    """Launch a new bot task based on provided parameters and data.

    Args:
        id_ (int): Bot identifier.
        system (str): Name of the system the bot belongs to.
        typebot (str): Type of bot to be launched.

    Returns:
        Response: A JSON response with success or error message and corresponding HTTP status code.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    message = {"success": "success"}
    is_started = 200

    async with app.app_context():
        try:
            # Parse and normalize input data from multiple possible formats.
            request_data = await request.data
            request_form = await request.form
            request_json = await request.json

            data_bot = (request_json if isinstance(request_data, bytes) else request_data) or request_form

            if isinstance(data_bot, bytes):
                data_bot = data_bot.decode("utf-8")

            if isinstance(data_bot, str):
                # Clean and decode JSON string input.
                data_bot = data_bot.replace("\\", "").replace("'", "")
                data_bot = json.loads(data_bot)
                if not isinstance(data_bot, dict):
                    raise ValueError("Invalid data_bot format")

            files = await request.files
            celery_app: Celery = app.extensions["celery"]
            # Execute the bot task launch.
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
            is_started = 500

    return await make_response(jsonify(message), is_started)


@bot.post("/periodic_bot/<id_>/<system>/<typebot>")
async def periodic_bot(id_: int, system: str, typebot: str) -> Response:
    """Schedule a bot for periodic execution.

    Processes request input for scheduling recurring bot tasks.

    Args:
        id_ (int): Bot identifier.
        system (str): Name of the system for scheduling.
        typebot (str): Type of bot to schedule.

    Returns:
        Response: A JSON response indicating success or, in case of errors, details of the exception.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    message = {"success": "success"}
    is_started = 200

    async with app.app_context():
        try:
            # Process different request data formats.
            request_data = await request.data
            request_form = await request.form
            request_json = bytes(await request.json, "utf-8").decode("unicode_escape")
            data_bot = (request_json if isinstance(request_data, bytes) else request_data) or request_form

            if isinstance(data_bot, bytes):
                data_bot = data_bot.decode("utf-8")
            if isinstance(data_bot, str):
                # Clean and parse string input into JSON.
                data_bot = data_bot.replace("\\", "").replace("'", "")
                data_bot = json.loads(data_bot)
                if not isinstance(data_bot, dict):
                    raise ValueError("Invalid data_bot format")

            files = await request.files

            # Schedule the bot task execution.
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
            is_started = 500

    return await make_response(jsonify(message), is_started)
