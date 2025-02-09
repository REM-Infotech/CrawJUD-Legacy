"""Module for botlaunch route."""

import json
import os
import traceback  # noqa: F401
from contextlib import suppress
from datetime import date, datetime  # noqa: F401
from pathlib import Path  # noqa: F401
from typing import Any, Union  # noqa: F401

import aiofiles
import httpx
from flask_sqlalchemy import SQLAlchemy
from quart import (  # noqa: F401
    Blueprint,
    Response,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from quart import current_app as app  # noqa: F401
from quart_auth import login_required  # noqa: F401
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ...forms import BotForm
from ...misc import (
    MakeModels,  # noqa: F401
    generate_pid,
)
from ...models import BotsCrawJUD, Credentials, LicensesUsers, Servers

FORM_CONFIGURATOR = {
    "JURIDICO": {
        "file_auth": ["xlsx", "creds", "state", "confirm_fields"],
        "multipe_files": ["xlsx", "creds", "state", "otherfiles", "confirm_fields"],
        "only_file": ["xlsx", "state", "confirm_fields"],
        "pautas": ["data_inicio", "data_fim", "creds", "state", "varas"],
        "proc_parte": [
            "parte_name",
            "doc_parte",
            "data_inicio",
            "data_fim",
            "polo_parte",
            "state",
            "varas",
            "creds",
        ],
    },
    "ADMINISTRATIVO": {
        "file_auth": ["xlsx", "creds", "client", "confirm_fields"],
        "multipe_files": ["xlsx", "creds", "client", "otherfiles", "confirm_fields"],
    },
    "INTERNO": {"multipe_files": ["xlsx", "otherfiles"]},
}


async def get_bot_info(db: SQLAlchemy, id: int) -> BotsCrawJUD | None:  # noqa: A002
    """Retrieve bot information from the database."""
    return (
        db.session.query(BotsCrawJUD)
        .select_from(LicensesUsers)
        .join(LicensesUsers.bots)
        .filter(LicensesUsers.license_token == session["license_token"])
        .filter(BotsCrawJUD.id == id)
        .first()
    )


async def get_form_data(
    db: SQLAlchemy, system: str, typebot: str, bot_info: BotsCrawJUD
) -> tuple[list[tuple], list[tuple], list[tuple[Any, Any]], list]:
    """Retrieve form data including states, clients, credentials, and form configuration."""
    states = [
        (state.state, state.state)
        for state in BotsCrawJUD.query.filter(
            BotsCrawJUD.type == typebot.upper(),
            BotsCrawJUD.system == system.upper(),
        ).all()
    ]

    clients = [
        (client.client, client.client)
        for client in BotsCrawJUD.query.filter(
            BotsCrawJUD.type == typebot.upper(),
            BotsCrawJUD.system == system.upper(),
        ).all()
    ]

    creds = (
        db.session.query(Credentials)
        .join(LicensesUsers)
        .filter(LicensesUsers.license_token == session["license_token"])
        .all()
    )

    credts = [
        (credential.nome_credencial, credential.nome_credencial)
        for credential in creds
        if credential.system == system.upper()
    ]

    form_config = []
    classbot = str(bot_info.classification)
    form_setup = str(bot_info.form_cfg)

    if typebot.upper() == "PAUTA" and system.upper() == "PJE":
        form_setup = "pautas"
    elif typebot.lower() == "proc_parte":
        form_setup = "proc_parte"

    form_config.extend(FORM_CONFIGURATOR[classbot][form_setup])

    chk_typebot = typebot.upper() == "PROTOCOLO"
    chk_state = bot_info.state == "AM"
    chk_system = system.upper() == "PROJUDI"
    if all([chk_typebot, chk_state, chk_system]):
        form_config.append("password")

    return states, clients, credts, form_config


async def process_form_submission(
    form: BotForm, system: str, typebot: str, bot_info: BotsCrawJUD
) -> tuple[dict, dict, str]:
    """Process form submission and prepare data and files for sending."""
    data = {}
    pid = generate_pid()
    data.update({"pid": pid, "user": session["login"]})

    temporarypath = app.config["TEMP_PATH"]
    data_form = form.data.items()
    files = {}

    for item, value in data_form:
        if isinstance(value, FileStorage):
            handle_file_storage(value, data, files, temporarypath)
            continue
        elif isinstance(value, list):
            handle_file_list(item, value, data, files, temporarypath)
            continue

        handle_other_data(item, value, data, system, typebot, bot_info, files)

    return data, files, pid


async def handle_file_storage(value: FileStorage, data: dict, files: dict, temporarypath: str | Path) -> None:
    """Handle file storage for form submission."""
    data.update({"xlsx": secure_filename(value.filename)})
    path_save = os.path.join(temporarypath, secure_filename(value.filename))
    value.save(path_save)
    buff = aiofiles.open(os.path.join(temporarypath, secure_filename(value.filename)), "rb")
    buff.seek(0)
    files.update({
        secure_filename(value.filename): (
            secure_filename(value.filename),
            buff,
            value.mimetype,
        )
    })


async def handle_file_list(
    item: str,
    value: FileStorage | str,
    data: dict,
    files: dict,
    temporarypath: str | Path,
) -> None:
    """Handle list of files for form submission."""
    if not isinstance(value[0], FileStorage):
        data.update({item: value})
        return

    for filev in value:
        if isinstance(filev, FileStorage):
            filev.save(os.path.join(temporarypath, secure_filename(filev.filename)))
            buff = aiofiles.open(os.path.join(temporarypath, secure_filename(filev.filename)), "rb")
            files.update({
                secure_filename(filev.filename): (
                    secure_filename(filev.filename),
                    buff,
                    filev.mimetype,
                )
            })


async def handle_other_data(
    item: str,
    value: str,
    data: str,
    system: str,
    typebot: str,
    bot_info: BotsCrawJUD,
    files: dict = None,
) -> None:
    """Handle other types of data for form submission."""
    if item == "creds":
        handle_credentials(value, data, system, files)
    else:
        if not data.get(item):
            data.update({item: value})
        if isinstance(value, date):
            data.update({item: value.strftime("%Y-%m-%d")})

        chks = [
            system.upper() == "PROJUDI",
            typebot.upper() == "PROTOCOLO",
            bot_info.state == "AM",
            item == "password",
        ]
        if all(chks):
            data.update({"token": value})


async def handle_credentials(value: str, data: dict, system: str, files: dict) -> None:
    """Handle credentials for form submission."""
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    temporarypath = app.config["TEMP_PATH"]
    creds = (
        db.session.query(Credentials)
        .join(LicensesUsers)
        .filter(LicensesUsers.license_token == session["license_token"])
        .all()
    )
    for credential in creds:
        if credential.nome_credencial == value:
            if credential.login_method == "pw":
                data.update({
                    "username": credential.login,
                    "password": credential.password,
                    "login_method": credential.login_method,
                })
            elif credential.login_method == "cert":
                certpath = os.path.join(temporarypath, credential.certficate)
                with aiofiles.open(certpath, "wb") as f:
                    f.write(credential.certficate_blob)
                buff = aiofiles.open(os.path.join(certpath), "rb")
                files.update({
                    credential.certficate: (
                        credential.certficate,
                        buff,
                    )
                })
                data.update({
                    "username": credential.login,
                    "name_cert": credential.certficate,
                    "token": credential.key,
                    "login_method": credential.login_method,
                })
            break


async def send_data_to_servers(data: dict, files: dict, headers: dict, pid: str) -> Response | None:
    """Send data to servers and handle the response."""
    servers = Servers.query.all()
    for server in servers:
        data.update({"url_socket": server.address})
        kwargs = {
            "url": f"https://{server.address}{request.path}",
            "json": json.dumps(data),
        }
        if files:
            kwargs.pop("json")
            kwargs.update({"files": files, "data": data})
        response = None
        async with suppress(Exception):
            async with httpx.AsyncClient() as client:
                response = await client.post(**kwargs, headers=headers)
        if response:
            if response.status_code == 200:
                message = f"Execução iniciada com sucesso! PID: {pid}"
                flash(message, "success")
                return await make_response(redirect(url_for("logsbot.logs_bot", pid=pid)))
            elif response.status_code == 500:
                pass
    flash("Erro ao iniciar robô", "error")
    return None


async def handle_form_errors(form: BotForm) -> None:
    """Handle form validation errors."""
    if form.errors:
        for field_err in form.errors:
            for error in form.errors[field_err]:
                flash(f"Erro: {error}", "error")
