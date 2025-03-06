"""Module for log routes.

This module defines endpoints for managing logs and controlling bot executions.
"""

import asyncio
import json
from os import environ, getenv
from pathlib import Path

import httpx as requests
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Response,
    abort,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from quart import current_app as app

from crawjud.decorators import login_required
from crawjud.misc import generate_signed_url
from crawjud.models import Executions, LicensesUsers, Users
from crawjud.utils.status import TaskExec

from . import logsbot


def stopbot(user: str, pid: str, socket: str) -> None:
    """Stop a bot by sending a POST request to the stop endpoint.

    Args:
        user (str): The username.
        pid (str): The process identifier.
        socket (str): The socket URL.

    """
    requests.post(url=f"{socket}/stop/{user}/{pid}", timeout=300)


@logsbot.context_processor
async def setpid_socket() -> dict[str, str | None]:
    """Provide 'pid' and 'socket_bot' cookie values to the template context.

    Returns:
        dict: A dictionary with 'pid' and 'socket_bot' keys.

    """
    pid = request.cookies.get("pid")
    socket_bot = request.cookies.get("socket_bot")

    return {"pid": pid, "socket_bot": socket_bot}


@logsbot.route("/logs_bot/<pid>")
@login_required
async def logs_bot(pid: str) -> Response:
    """Render the logs bot page for the specified execution.

    Args:
        pid (str): The process identifier.

    Returns:
        Response: A Quart response rendering the logs bot page.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    async with app.app_context():
        try:
            # Load cached data for the room to send previous logs, if any.
            from crawjud.bot import WorkerBot
            from crawjud.models import ThreadBots

            process_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()

            message = "Fim da Execução"

            if process_id:
                process_id = process_id.processID

                # Check the current status of the bot.
                message = await WorkerBot.check_status(process_id, pid, app)

                if message != "Process running!":
                    # Update the data with a final log message.
                    cwd = Path(__file__).cwd()
                    join_path_pid = cwd.joinpath("crawjud", "bot", "temp", f"{pid}").resolve()
                    path_flag = join_path_pid.joinpath(f"{pid}.flag").resolve()

                    json_file = join_path_pid.joinpath(f"{pid}.json")
                    schedule_ask = None

                    if json_file.exists():
                        with json_file.open("r") as f:
                            schedule_ask = json.load(f).get("schedule", "False")

                    if not schedule_ask:
                        schedule_ask = "False"

                    data = {
                        "status": "Finalizado",
                        "schedule": schedule_ask,
                        "pid": pid,
                    }

                    await TaskExec.task_exec(
                        data=data,
                        exec_type="stop",
                        app=app,
                        path_flag=path_flag,
                    )
                    await flash("Execução encerrada!", "success")

        except Exception as e:
            app.logger.exception("An error occurred: %s", str(e))

    if not session.get("license_token"):
        await flash("Sessão expirada. Faça login novamente.", "error")
        return await make_response(
            redirect(
                url_for(
                    "auth.login",
                ),
            )
        )

    title = f"Execução {pid}"
    user_id = Users.query.filter(Users.login == session["login"]).first().id
    execution = db.session.query(Executions).join(Users, Users.id == user_id).filter(Executions.pid == pid).first()

    admin_cookie, supersu_cookie = None, None

    admin_cookie = request.cookies.get("roles_admin")
    supersu_cookie = request.cookies.get("roles_supersu")

    if admin_cookie and not supersu_cookie:
        if json.loads(admin_cookie).get("login_id") == session["_id"]:
            execution = (
                db.session.query(Executions)
                .join(Users)
                .join(LicensesUsers)
                .filter(
                    LicensesUsers.license_token == session["license_token"],
                    Executions.pid == pid,
                )
                .first()
            )

    elif supersu_cookie:
        if json.loads(supersu_cookie).get("login_id") == session["_id"]:
            execution = Executions.query.filter(Executions.pid == pid).first()

    if execution is None:
        return await make_response(
            redirect(
                f"{url_for('exe.executions')}",
            ),
        )

    if execution.status == "Finalizado":
        return await make_response(
            redirect(
                f"{url_for('exe.executions')}?pid={pid}",
            ),
        )

    rows = execution.total_rows
    resp = await make_response(
        await render_template(
            "index.html",
            page="logs_bot.html",
            pid=pid,
            total_rows=rows,
            title=title,
        )
    )

    resp.set_cookie(
        "socket_bot",
        environ.get("URL_WEB"),
        max_age=60 * 60 * 24,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    resp.set_cookie("pid", pid, max_age=60 * 60 * 24, httponly=True, secure=True, samesite="Lax")
    return resp


@logsbot.route("/stop_bot/<pid>", methods=["GET"])
@login_required
async def stop_bot(pid: str) -> Response:
    """Stop the bot execution and wait until it has finished.

    Args:
        pid (str): The process identifier.

    Returns:
        Response: A Quart redirect response to the executions page.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    socket = request.cookies.get("socket_bot")
    stopbot(session["login"], pid, f"https://{socket}")

    is_stopped = True

    while is_stopped:
        execut = db.session.query(Executions).filter(Executions.pid == pid).first()

        if str(execut.status).lower() == "finalizado":
            is_stopped = False

        asyncio.sleep(2)

    await flash("Execução encerrada", "success")
    return await make_response(
        redirect(
            url_for(
                "exe.executions",
            ),
        ),
    )


@logsbot.route("/status/<pid>", methods=["GET"])
@login_required
async def status(pid: str) -> Response:
    """Check the status of an execution and return its result.

    Args:
        pid (str): The process identifier.

    Returns:
        Response: A Quart JSON response with execution status or error message.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    i = 0
    if not session.get("license_token"):
        abort(405, description="Sessão expirada. Faça login novamente.")

    response_data = {"erro": "erro"}

    while i <= 5:
        user_id = Users.query.filter(Users.login == session["login"]).first().id
        execution = (
            db.session.query(Executions)
            .join(Users, Users.id == user_id)
            .filter(
                Executions.pid == pid,
            )
            .first()
        )

        admin_cookie, supersu_cookie = None, None

        admin_cookie = request.cookies.get("roles_admin")
        supersu_cookie = request.cookies.get("roles_supersu")

        if admin_cookie and not supersu_cookie:
            if json.loads(admin_cookie).get("login_id") == session["_id"]:
                execution = (
                    db.session.query(Executions)
                    .join(Users)
                    .join(LicensesUsers)
                    .filter(
                        LicensesUsers.license_token == session["license_token"],
                        Executions.pid == pid,
                    )
                    .first()
                )

        elif supersu_cookie:
            if json.loads(supersu_cookie).get("login_id") == session["_id"]:
                execution = db.session.query(Executions).filter(Executions.pid == pid).first()

        if execution.status and execution.status == "Finalizado":
            signed_url = generate_signed_url(execution.file_output)
            response_data = {"message": "OK", "document_url": signed_url}
            return await make_response(
                jsonify(
                    response_data,
                ),
                200,
            )

        await asyncio.sleep(1.5)
        i += 1

    return await make_response(
        jsonify(
            response_data,
        ),
        500,
    )


@logsbot.route("/url_server/<pid>", methods=["GET"])
@login_required
async def url_server(pid: str) -> Response:
    """Retrieve the server URL associated with the given execution.

    Args:
        pid (str): The process identifier.

    Returns:
        Response: A Quart JSON response containing the server URL.

    """
    return await make_response(
        jsonify(
            {"url_server": getenv("URL_WEB")},
        ),
    )
