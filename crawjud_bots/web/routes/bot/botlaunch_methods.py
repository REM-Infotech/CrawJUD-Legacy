"""Module for botlaunch route."""

import json
import os
from contextlib import suppress  # , asynccontextmanager
from datetime import date, datetime, time
from pathlib import Path
from typing import Any  # , AsyncGenerator

import aiofiles
import httpx
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Response,
    flash,
    make_response,
    redirect,
    request,
    session,
    url_for,
)
from quart import current_app as app
from quart.datastructures import FileStorage
from werkzeug.utils import secure_filename
from wtforms import FieldList, FileField

from ....forms import BotForm
from ....misc import (
    generate_pid,
)
from ....models import BotsCrawJUD, Credentials, LicensesUsers, Servers

FORM_CONFIGURATOR = {
    "JURIDICO": {
        "only_auth": ["creds", "state", "periodic_task", "periodic_task_group"],
        "file_auth": ["xlsx", "creds", "state", "confirm_fields", "periodic_task", "periodic_task_group"],
        "multipe_files": [
            "xlsx",
            "creds",
            "state",
            "otherfiles",
            "confirm_fields",
            "periodic_task",
            "periodic_task_group",
        ],
        "only_file": ["xlsx", "state", "confirm_fields", "periodic_task", "periodic_task_group"],
        "pautas": ["data_inicio", "data_fim", "creds", "state", "varas", "periodic_task", "periodic_task_group"],
        "proc_parte": [
            "parte_name",
            "doc_parte",
            "data_inicio",
            "data_fim",
            "polo_parte",
            "state",
            "varas",
            "creds",
            "periodic_task",
            "periodic_task_group",
        ],
    },
    "ADMINISTRATIVO": {
        "file_auth": ["xlsx", "creds", "client", "confirm_fields", "periodic_task", "periodic_task_group"],
        "multipe_files": [
            "xlsx",
            "creds",
            "client",
            "otherfiles",
            "confirm_fields",
            "periodic_task",
            "periodic_task_group",
        ],
    },
    "INTERNO": {"multipe_files": ["xlsx", "otherfiles"]},
}


def get_bot_info(db: SQLAlchemy, id_: int) -> BotsCrawJUD | None:
    """Retrieve bot information from the database."""
    return (
        db.session.query(BotsCrawJUD)
        .select_from(LicensesUsers)
        .join(LicensesUsers.bots)
        .filter(LicensesUsers.license_token == session["license_token"])
        .filter(BotsCrawJUD.id == id_)
        .first()
    )


def get_form_data(
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


async def process_form_submission_periodic(
    form: BotForm, system: str, typebot: str, bot_info: BotsCrawJUD
) -> tuple[dict, dict, str, bool]:
    """Process form submission for periodic tasks and prepare data and files for sending."""
    data = {}
    pid = generate_pid()
    data.update({"pid": pid, "user": session["login"]})
    data_fields = form._fields.items()
    files = {}
    temporarypath = crawjud_bots.app.config["TEMP_DIR"]
    for field_name, field in data_fields:
        value = field.data
        item = field_name
        if isinstance(field, FileField):
            await handle_file_storage(value, data, files, temporarypath)
            continue

        if isinstance(field, FieldList):
            for pfield in field.data:
                pfield: dict[str, str | datetime | list[str]] = pfield
                field_itens = list(pfield.items())
                for key, val in field_itens:
                    if key == "csrf_token":
                        continue

                    if key == "days" and len(val) == 0:
                        val = "*"

                    if isinstance(val, time):
                        val = str(val.strftime("%H:%M"))
                    await handle_other_data(key, val, data, system, typebot, bot_info, files)

        elif isinstance(field, list) and all(isinstance(val, FileStorage) for val in field.data):
            for val in field.data:
                await handle_file_storage(val, data, files, temporarypath)

            continue

        else:
            await handle_other_data(item, value, data, system, typebot, bot_info, files)

    return data, files, pid, True


async def process_form_submission(
    form: BotForm,
    system: str,
    typebot: str,
    bot_info: BotsCrawJUD,
) -> tuple[dict, dict, str]:
    """Process form submission and prepare data and files for sending."""
    data = {}
    pid = generate_pid()
    data.update({"pid": pid, "user": session["login"]})

    temporarypath = crawjud_bots.app.config["TEMP_DIR"]
    data_form = form.data.items()
    files = {}

    for item, value in data_form:
        if item == "periodic_task":
            continue

        if isinstance(value, FileStorage):
            await handle_file_storage(value, data, files, temporarypath)
            continue
        if isinstance(value, list) and all(isinstance(val, FileStorage) for val in value):
            for val in value:
                await handle_file_storage(val, data, files, temporarypath)

            continue

        await handle_other_data(item, value, data, system, typebot, bot_info, files)

    return data, files, pid


async def handle_file_storage(value: FileStorage, data: dict, files: dict, temporarypath: str | Path) -> None:
    """Handle file storage for form submission."""
    data.update({"xlsx": secure_filename(value.filename)})
    path_save = Path(temporarypath).joinpath(secure_filename(value.filename))
    await value.save(path_save)

    async with aiofiles.open(path_save, "rb") as f:
        file_buffer = FileStorage(
            await f.read(),
            filename=path_save.name,
            content_type=value.mimetype,
            content_length=path_save.stat().st_size,
        )
    files.update({
        file_buffer.filename: (
            file_buffer.filename,
            file_buffer.stream,
            file_buffer.mimetype,
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


def handle_credentials(value: str, data: dict, system: str, files: dict) -> None:
    """Handle credentials for form submission."""
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    temporarypath = crawjud_bots.app.config["TEMP_DIR"]
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
                with open(certpath, "wb") as f:
                    f.write(credential.certficate_blob)
                buff = open(os.path.join(certpath), "rb")
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


async def send_data_to_servers(
    data: dict,
    files: dict,
    headers: dict,
    pid: str,
    periodic_bot: bool = False,
) -> Response | None:
    """Send data to servers and handle the response."""
    servers = Servers.query.all()
    for server in servers:
        data.update({"url_socket": server.address})

        request_path = request.path
        if periodic_bot:
            request_path = request_path.replace("/bot", "/periodic_bot")
        elif not periodic_bot:
            if data.get("periodic_task_group"):
                data.pop("periodic_task_group")

        arguments = {
            "url": f"https://{server.address}{request_path}",
            "json": json.dumps(data),
        }
        if files:
            arguments.pop("json")
            arguments.update({"files": files, "data": data})

        response = None
        with suppress(Exception):
            async with httpx.AsyncClient() as client:
                response = await client.post(**arguments, headers=headers)
        if response:
            if response.status_code == 200:
                message = f"Execução iniciada com sucesso! PID: {pid}"
                await flash(message, "success")

                if periodic_bot:
                    return await make_response(
                        redirect(
                            url_for(
                                "dash.dashboard",
                            ),
                        )
                    )

                return await make_response(
                    redirect(
                        url_for(
                            "logsbot.logs_bot",
                            pid=pid,
                        ),
                    ),
                )
    await flash("Erro ao iniciar robô", "error")
    return None


async def handle_form_errors(form: BotForm) -> None:
    """Handle form validation errors."""
    if form.errors:
        for field_err in form.errors:
            for error in form.errors[field_err]:
                await flash(f"Erro: {error}", "error")
