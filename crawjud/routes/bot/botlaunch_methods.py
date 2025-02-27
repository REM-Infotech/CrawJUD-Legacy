"""Module for botlaunch route."""

import mimetypes  # noqa: F401
from datetime import date, datetime, time  # noqa: F401
from pathlib import Path  # noqa: F401
from typing import Any, Union  # , AsyncGenerator

from celery import Celery, Task
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Response,
    flash,
    make_response,
    redirect,
    session,
    url_for,
)
from quart import current_app as app
from quart.datastructures import FileStorage  # noqa: F401
from werkzeug.utils import secure_filename  # noqa: F401
from wtforms import FieldList, FileField, FormField, MultipleFileField, TimeField  # noqa: F401

from crawjud.models.bots import ThreadBots
from crawjud.types import AnyType, Numbers, strings
from crawjud.utils.status import TaskExec

from ...forms import BotForm
from ...misc import (
    generate_pid,  # noqa: F401
)
from ...models import BotsCrawJUD, Credentials, LicensesUsers

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


def handle_credentials(value: str, data: dict, system: str, files: dict) -> None:
    """Handle credentials for form submission."""
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    temporarypath = app.config["TEMP_DIR"]
    creds = (
        db.session.query(Credentials)
        .join(LicensesUsers)
        .filter(LicensesUsers.license_token == session["license_token"])
        .all()
    )
    for credential in creds:
        if all([
            credential.nome_credencial == value,
            credential.system == system.upper(),
        ]):
            if credential.login_method == "pw":
                data.update({
                    "username": credential.login,
                    "password": credential.password,
                    "login_method": credential.login_method,
                })
            elif credential.login_method == "cert":
                cert_path = Path(temporarypath).joinpath(credential.certficate)
                with cert_path.open("wb") as f:
                    f.write(credential.certficate_blob)

                content_type = mimetypes.guess_type(cert_path)
                content_lenght = cert_path.stat().st_size
                credential_object = FileStorage(
                    cert_path.open("rb"),
                    filename=credential.certficate,
                    content_type=content_type,
                    content_length=content_lenght,
                )
                files.update({credential.certficate: credential_object})
                data.update({
                    "username": credential.login,
                    "name_cert": credential.certficate,
                    "token": credential.key,
                    "login_method": credential.login_method,
                })
            break


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


def perform_submited_form(
    form: BotForm,
    data: dict,
    files: dict,
    system: str,
    typebot: str,
) -> None:
    """Perform the submitted form."""
    form_data = form._fields.items()
    for field_name, attributes_field in form_data:
        data_field: Union[
            strings,
            Numbers,
            FileStorage,
        ] = attributes_field.data

        if isinstance(attributes_field, FileField):
            files.update({data_field.filename: data_field})
            continue

        elif isinstance(attributes_field, MultipleFileField):
            for file_ in data_field:
                files.update({file_.filename: file_})
            continue

        elif isinstance(attributes_field, FieldList):
            for entry in attributes_field.entries:
                for formfield in entry.form:
                    perform_submited_form(formfield, data, files)
            continue

        elif field_name == "creds":
            handle_credentials(data_field, data, system, files)
            continue

        if isinstance(attributes_field, TimeField):
            data_field = data_field.strftime("%H:%M:%S")

        data.update({field_name: data_field})


async def setup_task_worker(
    id_: int,
    pid: str,
    form: BotForm,
    system: str,
    typebot: str,
    bot_info: BotsCrawJUD,
    **kwargs: AnyType,
) -> Response | None:
    """Send data to servers and handle the response."""
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        celery_app: Celery = app.extensions["celery"]

        user = session["login"]  # noqa: F841
        data: dict[str, str] = {}
        files: dict[str, FileStorage] = {}
        periodic_bot = False
        cls = TaskExec

        data, files, periodic_bot = perform_submited_form(form, data, files)

        path_pid = await cls.configure_path()
        data, path_args = await cls.args_tojson(
            path_pid=path_pid,
            pid=pid,
            id_=id_,
            system=system,
            typebot=typebot,
        )
        execut, display_name = await cls.insert_into_database

        kwargs_ = {
            "display_name": display_name,
            "system": system,
            "typebot": typebot,
            "path_args": path_args,
        }

        if periodic_bot:
            await cls.schedule_into_database(
                db,
                data,
                system=system,
                typebot=typebot,
                path_args=path_args,
                display_name=display_name,
            )

        elif not periodic_bot:
            task: Task = celery_app.send_task(f"crawjud.bot.{system.lower()}_launcher", kwargs=kwargs_)
            process_id = str(task.id)

            # Salva o ID no "banco de dados"
            add_thread = ThreadBots(pid=pid, processID=process_id)
            db.session.add(add_thread)
            db.session.commit()
            is_started = 200

        try:
            await cls.send_email(execut, app, "start")
        except Exception as e:
            app.logger.error("Error sending email: %s", str(e))

    except Exception as e:
        app.logger.error("Error starting bot: %s", str(e))
        is_started = 500

    if is_started == 200:
        await flash(message=f"Execução iniciada com sucesso! PID: {pid}")
        return await make_response(
            redirect(
                url_for(
                    "logs.logs_bot",
                    pid=pid,
                ),
            ),
        )

    elif is_started != 200:
        await flash("Erro ao iniciar a execução!", "error")
        return await make_response(
            redirect(
                url_for(
                    "bot.dashboard",
                ),
            ),
        )


async def handle_form_errors(form: BotForm) -> None:
    """Handle form validation errors."""
    if form.errors:
        for field_err in form.errors:
            for error in form.errors[field_err]:
                await flash(f"Erro: {error}", "error")
