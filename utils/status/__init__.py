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
from typing import Literal

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

from app.models import BotsCrawJUD, Executions, LicensesUsers, ThreadBots, Users

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
        path_pid.mkdir(parents=True, exist_ok=True, mode=777)

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
    ) -> tuple[dict[str, str | int | datetime], str]:
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

        if form is not None:
            for key, value in form.items():
                data.update({key: value})

        data.update({"id": id_, "system": system, "typebot": typebot})

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

        path_args = path.join(path_pid, f"{pid}.json")
        async with aiofiles.open(path_args, "w") as f:  # noqa: FURB103
            await f.write(json.dumps(data))

        return data, path_args

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
    ) -> dict[str, str | list[str]]:
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

        usr = db.session.query(Users).filter(Users.login == user).first()
        bt = db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == id_).first()
        license_ = db.session.query(LicensesUsers).filter_by(license_token=usr.licenseusr.license_token).first()

        execut.user = usr
        execut.bot = bt
        execut.license_usr = license_

        admins: list[str] = []
        pid = execut.pid

        display_name = str(execut.bot.display_name)
        xlsx = str(execut.arquivo_xlsx)

        try:
            for adm in usr.licenseusr.admins:
                admins.append(adm.email)

        except Exception:
            err = traceback.format_exc()
            logger.exception(err)

        exec_data: dict[str, str | list[str]] = {
            "pid": pid,
            "display_name": display_name,
            "xlsx": xlsx,
            "username": str(usr.nome_usuario),
            "email": str(usr.email),
            "admins": admins,
        }

        db.session.add(execut)
        db.session.commit()
        db.session.close()

        return exec_data

    @classmethod
    async def send_email(cls, execut: dict[str, str | list[str]], app: Quart, type_notify: str) -> None:
        """Send an email to the user.

        Args:
            execut (dict[str, str | list[str]]): The bot execution data.
            app (Quart): The Quart application instance.
            type_notify (str): The type of notification.

        """
        render_template = env.get_template
        mail = Mail(app)

        async with app.app_context():
            mail.connect()

        admins: list[str] = execut.get("admins")
        pid = execut.get("pid")

        display_name = execut.get("display_name")
        xlsx = execut.get("xlsx")
        destinatario = execut.get("email")
        username = execut.get("username")

        async with app.app_context():
            sendermail = environ["MAIL_DEFAULT_SENDER"]

            robot = f"Robot Notifications <{sendermail}>"
            assunto = f"Bot {display_name} - {type_notify}"
            url_web = environ.get(" URL_WEB")
            destinatario = destinatario
            mensagem = render_template(f"email_{type_notify}.jinja").render(
                display_name=display_name, pid=pid, xlsx=xlsx, url_web=url_web, username=username
            )

            msg = Message(assunto, sender=robot, recipients=[destinatario], html=mensagem)
            if destinatario not in admins:
                msg = Message(assunto, sender=robot, recipients=[destinatario], html=mensagem, cc=admins)

            mail.send(msg)
        return "Email enviado com sucesso!"

    @classmethod
    async def make_zip(cls, pid: str) -> str:
        """Create a ZIP file.

        Args:
            pid (str): The process identifier of the bot.

        """
        from ..gcs_mgmt import get_file

        filename = get_file(pid)

        if filename == "":
            filename = await asyncio.create_task(cls.send_file_gcs(makezip(pid)))
        return filename

    @classmethod
    async def send_file_gcs(cls, zip_file: str) -> str:
        """Send a file to Google Cloud Storage.

        Args:
            zip_file (str): The ZIP file to send.

        """
        return enviar_arquivo_para_gcs(zip_file)

    @classmethod
    async def send_stop_exec(
        cls,
        app: Quart,
        db: SQLAlchemy,
        pid: str,
        status: str,
        file_out: str,
    ) -> dict[str, str | list[str]] | tuple[dict[str, str], Literal[500]]:
        """Stop the bot and handle file uploads and database interactions.

        Args:
            app (Quart): Quart application instance.
            db (SQLAlchemy): SQLAlchemy database instance.
            pid (str): Process ID.
            status (str): Status of the bot.
            file_out (str): The output file.

        """
        try:
            admins: list[str] = []

            task_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()  # noqa: N806
            exec_info = db.session.query(Executions).filter(Executions.pid == pid).first()

            if task_id or exec_info:
                exec_info.status = status
                exec_info.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
                exec_info.file_output = file_out

                pid = exec_info.pid
                usr: Users = exec_info.user

                display_name = str(exec_info.bot.display_name)
                xlsx = str(exec_info.arquivo_xlsx)
                usr = exec_info.user

                for adm in usr.licenseusr.admins:
                    admins.append(adm.email)

                exec_data: dict[str, str | list[str]] = {
                    "pid": pid,
                    "display_name": display_name,
                    "xlsx": xlsx,
                    "username": str(usr.nome_usuario),
                    "email": str(usr.email),
                    "admins": admins,
                }

                db.session.commit()
                db.session.close()

                return exec_data

            elif not task_id:
                raise Exception("Execution not found!")

            return exec_info

        except Exception as e:
            app.logger.error("An error occurred: %s", str(e))
            return {"message": "An internal error has occurred!"}, 500


__all__ = [
    makezip,
    email_start,
    email_stop,
    enviar_arquivo_para_gcs,
    load_cache,
    FormatMessage,
]
