"""Module: status.

This module manages the status of bots (Start and Stop).
"""

from __future__ import annotations

import asyncio
import json
import logging
import traceback  # noqa: F401
import unicodedata
from datetime import datetime
from os import environ, path
from pathlib import Path

import aiofiles
import openpyxl
import pytz
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Environment, FileSystemLoader
from openpyxl.worksheet.worksheet import Worksheet
from quart import Quart
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.models import BotsCrawJUD, Executions, LicensesUsers, Users

from .makefile import makezip
from .send_email import email_start, email_stop
from .server_side import FormatMessage, load_cache
from .upload_zip import enviar_arquivo_para_gcs

url_cache = []
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve().joinpath("mail/templates")), autoescape=True)


class InstanceBot:
    def __init__(self) -> None:
        """Initialize the class."""

    # Utilities methods
    @classmethod
    async def format_string(cls, string: str) -> str:
        """Format a string to be a secure filename.

        Args:
            string (str): The string to format.

        Returns:
                str: The formatted string.

        """
        return secure_filename(
            "".join([c for c in unicodedata.normalize("NFKD", string) if not unicodedata.combining(c)]),
        )

    # Tasks
    @classmethod
    async def configure_path(cls, app: Quart, pid: str, files: dict[str, FileStorage] = None) -> Path:
        """Configure the path for the bot.

        Args:
            app (Quart): The Quart application instance.
            pid (str): The process identifier of the bot.
            files (dict[str, FileStorage], optional): A dictionary containing file data. Defaults to None.

        """
        path_pid = Path(__file__).cwd().joinpath(app.config["TEMP_PATH"]).joinpath(pid).resolve()
        path_pid.mkdir(parents=True, exist_ok=True)

        if files is not None:
            for f, value in files.items():
                if "xlsx" not in f:
                    f = await cls.format_string(f)

                filesav = path_pid.joinpath(f)
                await value.save(filesav)

        return path_pid

    @classmethod
    async def args_tojson(
        cls,
        path_pid: Path,
        pid: str,
        id_: int,
        system: str,
        typebot: str,
        form: dict[str, str] = None,
        *args: tuple[str],
        **kwargs: dict[str, any],
    ) -> dict[str, str]:
        """Convert the bot arguments to a JSON file.

        Args:
            path_pid (Path): The path to the bot's arguments file.
            pid (str): The process identifier of the bot.
            id_ (int): The bot ID.
            system (str): The system name.
            typebot (str): The type of bot.
            form (dict[str, str], optional): A dictionary containing form data. Defaults to None.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        data: dict[str, str | int | datetime] = {}

        path_args = path_pid.joinpath(f"{pid}.json")
        if form is not None:
            for key, value in form.items():
                data.update({key: value})

        data.update({"id": id, "system": system, "typebot": typebot})

        if data.get("xlsx"):
            input_file = path.join(path_pid, data["xlsx"])
            if path.exists(input_file):
                wb = openpyxl.load_workbook(filename=input_file)
                ws: Worksheet = wb.active
                rows = ws.max_row

        elif data.get("typebot") == "pauta":
            data_inicio_formated = datetime.strptime(data.get("data_inicio"), "%Y-%m-%d")

            data_fim_formated = datetime.strptime(data.get("data_fim"), "%Y-%m-%d")

            diff = data_fim_formated - data_inicio_formated
            rows = diff.days + 2

        elif data.get("typebot") == "proc_parte":
            rows = len(list(data.get("varas"))) + 1

        data.update({"total_rows": rows})

        async with aiofiles.open(Path(path_args), "w") as f:  # noqa: FURB103
            await f.write(json.dumps(data))

        return data

    @classmethod
    async def insert_into_database(
        cls,
        db: SQLAlchemy,
        data: dict[str, str | int | datetime],
        pid: str,
        id_: int,
        user: str,
        *args: tuple,
        **kwargs: dict,
    ) -> tuple[Executions, str]:
        """Insert the bot execution data into the database.

        Args:
            db (SQLAlchemy): The SQLAlchemy database instance.
            data (dict[str, str | int | datetime]): A dictionary containing the bot execution data.
            pid (str): The process identifier of the bot.
            id_ (int): The bot ID.
            user (str): The user login.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        name_column = Executions.__table__.columns["arquivo_xlsx"]
        max_length = name_column.type.length
        xlsx_ = str(data.get("xlsx", "Sem Arquivo"))

        if len(data.get("xlsx", "Sem Arquivo")) > int(max_length):
            xlsx_ = xlsx_[: int(max_length)]
        rows = data.get("total_rows")
        execut = Executions(
            pid=pid,
            status="Em Execução",
            arquivo_xlsx=xlsx_,
            url_socket=data.get("url_socket"),
            total_rows=rows,
            data_execucao=datetime.now(pytz.timezone("America/Manaus")),
            file_output="Arguardando Arquivo",
        )

        usr = Users.query.filter(Users.login == user).first()
        bt = db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == id_).first()
        license_ = LicensesUsers.query.filter(LicensesUsers.license_token == usr.licenseusr.license_token).first()

        execut.user = usr
        execut.bot = bt
        execut.license_usr = license_

        db.session.add(execut)
        db.session.commit()

        return execut, bt.display_name

    @classmethod
    async def send_email(cls, execut: Executions, app: Quart, type_notify: str) -> None:
        """Send an email to the user.

        Args:
            execut (Executions): The bot execution data.
            app (Quart): The Quart application instance.
            type_notify (str): The type of notification.

        """
        render_template = env.get_template
        mail = Mail(app)

        with app.app_context():
            mail.connect()

        admins: list[str] = []
        pid = execut.pid
        usr: Users = execut.user

        display_name = str(execut.bot.display_name)
        xlsx = str(execut.arquivo_xlsx)

        try:
            for adm in usr.licenseusr.admins:
                admins.append(adm.email)

        except Exception:
            err = traceback.format_exc()
            logger.exception(err)

        with app.app_context():
            sendermail = environ["MAIL_DEFAULT_SENDER"]

            robot = f"Robot Notifications <{sendermail}>"
            assunto = f"Bot {display_name} - {type_notify}"
            url_web = environ.get(" URL_WEB")
            destinatario = usr.email
            username = str(usr.nome_usuario)
            mensagem = render_template(f"email_{type_notify}.html").render(
                display_name=display_name, pid=pid, xlsx=xlsx, url_web=url_web, username=username
            )

            msg = Message(assunto, sender=robot, recipients=[destinatario], html=mensagem)
            if usr.email not in admins:
                msg = Message(assunto, sender=robot, recipients=[destinatario], html=mensagem, cc=admins)

            mail.send(msg)
        return "Email enviado com sucesso!"

    @classmethod
    async def make_zip(cls, pid: str) -> str:
        """Create a ZIP file.

        Args:
            pid (str): The process identifier of the bot.

        """
        return makezip(pid)

    @classmethod
    async def send_file_gcs(cls, zip_file: str) -> None:
        """Send a file to Google Cloud Storage.

        Args:
            zip_file (str): The ZIP file to send.

        """
        return enviar_arquivo_para_gcs(zip_file)

    @classmethod
    async def send_stop_exec(
        cls,
        db: SQLAlchemy,
        pid: str,
        status: str,
        file_out: str,
    ) -> None:
        """Stop the bot and handle file uploads and database interactions.

        Args:
            db (SQLAlchemy): SQLAlchemy database instance.
            pid (str): Process ID.
            status (str): Status of the bot.
            file_out (str): The output file.

        """
        execution = Executions.query.filter(Executions.pid == pid).first()
        execution.status = status
        execution.file_output = file_out
        execution.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
        db.session.commit()
        db.session.close()


class SetStatus:
    """A class to manage  the status of bots (Start and Stop)."""


async def stop_execution(app: Quart, pid: str, robot_stop: bool = False) -> tuple[dict[str, str], int]:
    """Stop the execution of a bot based on its PID.

    Args:
        app (Quart): The Quart application instance.
        pid (str): The process identifier of the bot.
        robot_stop (bool, optional): Flag to indicate robot stop. Defaults to False.

    Returns:
        tuple[dict[str, str], int]: A message and HTTP status code.

    """
    async with app.app_context():
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        from app.models import Executions, ThreadBots

        from ..gcs_mgmt import get_file

        try:
            task_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()  # noqa: N806
            get_info = db.session.query(Executions).filter(Executions.pid == pid).first()

            if task_id or get_info:
                # Stop bot

                system = get_info.bot.system
                typebot = get_info.bot.type
                user = get_info.user.login
                get_info.status = "Finalizado"
                get_info.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
                filename = get_file(pid, app)

                if filename != "":
                    get_info.file_output = filename
                    db.session.commit()
                    db.session.close()

                elif filename == "":
                    bot_stop = SetStatus()
                    setup_stop = await asyncio.create_task(
                        bot_stop.config(usr=user, pid=pid, system=system, typebot=typebot)
                    )
                    get_info.file_output = await asyncio.create_task(setup_stop.botstop(db, app))
                    db.session.commit()
                    db.session.close()

            elif not task_id:
                raise Exception("Execution not found!")

            return {"message": "bot stopped!"}, 200

        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            return {"message": "An internal error has occurred!"}, 500


__all__ = [
    SetStatus,
    makezip,
    email_start,
    email_stop,
    enviar_arquivo_para_gcs,
    load_cache,
    FormatMessage,
    stop_execution,
]
