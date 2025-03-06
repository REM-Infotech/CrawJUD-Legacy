"""Module: status.

This module manages the status of bots (Start and Stop).
"""

from __future__ import annotations

import json
import logging
import traceback
import unicodedata
from datetime import datetime
from os import environ, getcwd
from pathlib import Path
from typing import Literal

import aiofiles
import openpyxl
import pytz
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Environment, FileSystemLoader
from openpyxl.worksheet.worksheet import Worksheet
from quart import Quart, session
from quart.datastructures import FileStorage
from werkzeug.utils import secure_filename

from crawjud.models import BotsCrawJUD, CrontabModel, Executions, LicensesUsers, ScheduleModel, ThreadBots, Users

from .makefile import makezip
from .permalink import generate_signed_url
from .server_side import format_message_log, load_cache
from .upload_zip import enviar_arquivo_para_gcs

url_cache = []
logger = logging.getLogger(__name__)

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.resolve().joinpath("mail", "templates")),
    autoescape=True,
)


class TaskExec:
    """Manage bot status tracking, task execution, and notifications with database integration."""

    def __init__(self) -> None:
        """Initialize the TaskExec instance."""

    @classmethod
    async def task_exec(
        cls,
        app: Quart = None,
        db: SQLAlchemy = None,
        data: dict = None,
        *args: str | int,
        **kwargs: str | int,
    ) -> int:
        """Execute a bot task based on the execution type.

        Args:
            app (Quart): Quart application instance.
            db (SQLAlchemy): Database instance.
            data (dict): Bot data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            int: HTTP status code indicating the outcome.

        """
        try:
            async with app.app_context():
                pid = data.get("pid")
                if not pid:
                    return 500
                db: SQLAlchemy = app.extensions["sqlalchemy"]
                status = data.get("status")
                schedule = data.get("schedule")
                path_flag = kwargs.get("path_flag")

                filename, _ = await cls.make_zip(pid)
                execut = await cls.send_stop_exec(app, db, pid, status, filename)

                try:
                    await cls.send_email(execut, app, "stop", schedule=schedule)
                except Exception as e:
                    app.logger.exception("Error sending email: %s", str(e))

                if path_flag:
                    Path(path_flag).touch(exist_ok=True)
                return 200
        except Exception as e:
            app.logger.exception("An error occurred: %s", str(e))

        return 500

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

    @classmethod
    async def configure_path(
        cls,
        pid: str,
        files: dict[str, FileStorage] = None,
    ) -> Path:
        """Configure the path for the bot.

        Args:
            app (Quart): The Quart application instance.
            pid (str): The process identifier of the bot.
            files (dict[str, FileStorage], optional): A dictionary containing file data. Defaults to None.

        """
        path_pid = (
            Path(getcwd())
            .joinpath(
                "crawjud",
                "bot",
                "temp",
            )
            .joinpath(pid)
        )

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
        pid: str,
        typebot: str,
        path_pid: Path,
        data: dict[str, str | int | datetime],
        *args: str,
        **kwargs: str,
    ) -> Path:
        """Convert the bot arguments to a JSON file.

        Args:
            pid (str): The process identifier of the bot.
            typebot (str): The type of bot.
            path_pid (Path): The path to the bot's directory.
            data (dict[str, str | int | datetime]): The bot arguments.
            *args (tuple[str]): Variable length argument list.
            **kwargs (dict[str, str]): Arbitrary keyword arguments.

        """
        rows = 0
        if data.get("xlsx"):
            data.update({"xlsx": str(data.get("xlsx"))})
            input_file = Path(path_pid).joinpath(data.get("xlsx"))
            if input_file.exists():
                wb = openpyxl.load_workbook(filename=input_file)
                ws: Worksheet = wb.active
                rows = ws.max_row

        elif typebot == "pauta":
            data_inicio_formated = data.get("data_inicio")
            if not isinstance(data_inicio_formated, datetime.date):
                data_inicio_formated = datetime.strptime(data_inicio_formated, "%Y-%m-%d")

            data_fim_formated = data.get("data_fim")
            if not isinstance(data_fim_formated, datetime.date):
                data_fim_formated = datetime.strptime(data_fim_formated, "%Y-%m-%d")

            diff = data_fim_formated - data_inicio_formated
            rows = diff.days + 2

        elif typebot == "proc_parte":
            rows = len(list(data.get("varas"))) + 1

        data.update({"total_rows": rows})

        path_args = path_pid.joinpath(f"{pid}.json")
        async with aiofiles.open(path_args, "w") as f:
            await f.write(json.dumps(data))

        return path_args

    @classmethod
    async def schedule_into_database(
        cls,
        db: SQLAlchemy,
        data: dict[str, str | int | datetime],
        *args: str | int,
        **kwargs: str | int,
    ) -> dict[str, str | int | datetime]:
        """Insert the bot execution data into the database.

        Args:
            db (SQLAlchemy): The SQLAlchemy database instance.
            data (dict[str, str | int | datetime]): A dictionary containing the bot execution data.
            *args(tuple[Any | str]): Additional positional arguments.
            **kwargs(dict[str, Any]): Additional keyword arguments.

        """
        user = session["login"]

        system = kwargs.pop("system")
        path_args = kwargs.pop("path_args")
        display_name = kwargs.pop("display_name")
        typebot = kwargs.pop("typebot")

        license_ = (
            db.session.query(LicensesUsers)
            .select_from(Users)
            .join(Users, LicensesUsers.user)
            .filter(Users.login == user)
            .first()
        )

        exec_ = (
            db.session.query(Executions)
            .filter(
                Executions.pid == data.get("pid"),
            )
            .first()
        )

        days_list = data.get("days", ["mon"])
        days: str = ",".join(days_list if len(days_list) > 0 else ["mon"])
        hour_minute = datetime.strptime(data.get("hour_minute", "08:00:00"), "%H:%M:%S")
        cron = CrontabModel(day_of_week=days, hour=str(hour_minute.hour), minute=str(hour_minute.minute))

        task_name = data.get("task_name")
        task_schedule = "crawjud.bot.%s_launcher" % system.lower()
        args_ = json.dumps([])
        kwargs_ = json.dumps({
            "schedule": "True",
            "path_args": str(path_args),
            "display_name": display_name,
            "system": system,
            "typebot": typebot,
        })

        user = db.session.query(Users).filter(Users.login == user).first()

        new_schedule = ScheduleModel(
            email=data.get("email_notify"),
            name=task_name,
            task=task_schedule,
            args=args_,
            kwargs=kwargs_,
        )
        new_schedule.schedule = cron
        new_schedule.license_usr = license_
        new_schedule.exec = exec_
        new_schedule.user = user
        db.session.add(new_schedule)
        db.session.commit()

    @classmethod
    async def insert_into_database(
        cls,
        db: SQLAlchemy,
        pid: str,
        id_: int,
        user: str,
        bot_info: BotsCrawJUD,
        data: dict[str, str | int | datetime],
        *args: str | int,
        **kwargs: str | int,
    ) -> tuple[dict[str, str | list[str]], str]:
        """Insert the bot execution data into the database."""
        name_column = Executions.__table__.columns["arquivo_xlsx"]
        max_length = name_column.type.length
        xlsx_ = str(data.get("xlsx", "Sem Arquivo"))

        if len(data.get("xlsx", "Sem Arquivo")) > int(max_length):
            xlsx_ = xlsx_[: int(max_length)]
        rows = data.get("total_rows")

        execut = db.session.query(Executions).filter(Executions.pid == pid).first()
        usr = db.session.query(Users).filter(Users.login == user).first()
        bt = bot_info
        license_ = (
            db.session.query(LicensesUsers)
            .filter_by(
                license_token=usr.licenseusr.license_token,
            )
            .first()
        )
        if not execut:
            execut = Executions(
                pid=pid,
                status="Em Execução",
                arquivo_xlsx=xlsx_,
                url_socket=data.get("url_socket"),
                total_rows=rows,
                data_execucao=datetime.now(pytz.timezone("America/Sao_Paulo")),
                file_output="Arguardando Arquivo",
            )

            execut.user = usr
            execut.bot = bt
            execut.license_usr = license_
            db.session.add(execut)

        admins: list[str] = []

        display_name = str(bt.display_name)
        xlsx = str(xlsx_)

        try:
            with db.session.no_autoflush:
                for adm in license_.admins:
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

        db.session.commit()
        db.session.close()

        return exec_data, display_name

    @classmethod
    async def send_email(
        cls,
        execut: dict[str, str | list[str]],
        app: Quart,
        type_notify: str,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Send an email to the user.

        Args:
            execut (dict[str, str | list[str]]): The bot execution data.
            app (Quart): The Quart application instance.
            type_notify (str): The type of notification.
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

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
        scheduled = kwargs.get("schedule", "False")

        schedule_email = execut.get("email_notify", kwargs.get("email_notify"))

        async with app.app_context():
            sendermail = environ["MAIL_DEFAULT_SENDER"]

            robot = f"Robot Notifications <{sendermail}>"
            assunto = f"Bot {display_name} - {type_notify.capitalize()} Notification"
            url_web = environ.get("URL_WEB")
            destinatario = destinatario
            msg = Message(
                assunto,  # subject
                sender=robot,  # sender
                recipients=[destinatario],  # recipients
            )

            if scheduled == "False":
                msg.html = render_template(f"email_{type_notify}.jinja").render(
                    display_name=display_name,  # display name bot
                    pid=pid,  # pid bot
                    xlsx=xlsx,  # xlsx file
                    url_web=url_web,  # url web
                    username=username,  # username user
                )

            elif scheduled == "True" and type_notify == "stop":
                task_name = execut.get("task_name")
                msg.html = render_template("email_schedule.jinja").render(
                    task_name=task_name,
                    display_name=display_name,  # display name bot
                    pid=pid,  # pid bot
                    xlsx=xlsx,  # xlsx file
                    url_web=url_web,  # url web
                    username=username,  # username user
                    file_url=await cls.make_permalink(),  # permalink file
                )
                if schedule_email:
                    msg.recipients.append(schedule_email)
                # file_zip = Path(kwargs.get("file_zip"))
                # async with aiofiles.open(file_zip, "rb") as f:
                #     content_type = mimetypes.guess_type(str(file_zip))[0]
                #     content_size = file_zip.stat().st_size
                #     file_ = FileStorage(
                #         await f.read(),
                #         file_zip.name,  # file zip name
                #         file_zip.name,
                #         content_type=content_type,  # content type
                #         content_length=content_size,  # content length
                #     )
                #     msg.attach(
                #         file_zip.name,
                #         file_.content_type,
                #         await f.read(),
                #     )

            if destinatario not in admins:
                msg.cc.extend(admins)

            mail.send(msg)

        app.logger.info("Email enviado com sucesso!")
        return "Email enviado com sucesso!"

    @classmethod
    async def make_permalink(cls, pid: str) -> str:
        """Create a permalink for the bot output file."""
        from ..gcs_mgmt import get_file

        filename = get_file(pid)

        if filename == "":
            file_zip, f_path = makezip(pid)
            filename, _ = await cls.send_file_gcs(file_zip, f_path)

        return generate_signed_url(filename)

    @classmethod
    async def make_zip(cls, pid: str) -> tuple[str, Path | None]:
        """Create a ZIP file.

        Args:
            pid (str): The process identifier of the bot.

        """
        from ..gcs_mgmt import get_file

        filename = get_file(pid)
        file_path: Path = None

        if filename == "":
            file_zip, f_path = makezip(pid)
            filename, file_path = await cls.send_file_gcs(file_zip, f_path)
        return filename, file_path

    @classmethod
    async def send_file_gcs(cls, zip_file: str, file_path: Path) -> tuple[str, Path]:
        """Send a file to Google Cloud Storage.

        Args:
            zip_file (str): The ZIP file to send.
            file_path (Path): The path to the file.

        """
        file_zip1, file_path2 = enviar_arquivo_para_gcs(zip_file, file_path)
        return file_zip1, file_path2

    @classmethod
    async def send_stop_exec(
        cls,
        app: Quart,
        db: SQLAlchemy,
        pid: str,
        status: str,
        file_out: str,
        *args: str | int,
        **kwargs: str | int,
    ) -> dict[str, str | list[str]] | tuple[dict[str, str], Literal[500]]:
        """Stop the bot and handle file uploads and database interactions.

        Args:
            app (Quart): Quart application instance.
            db (SQLAlchemy): SQLAlchemy database instance.
            pid (str): Process ID.
            status (str): Status of the bot.
            file_out (str): The output file.
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        try:
            admins: list[str] = []

            task_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()
            exec_info = db.session.query(Executions).filter(Executions.pid == pid).first()
            email_notify = None

            if task_id or exec_info:
                exec_info.status = status
                exec_info.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
                exec_info.file_output = str(file_out)

                pid = exec_info.pid
                usr: Users = exec_info.user

                display_name = str(exec_info.bot.display_name)
                xlsx = str(exec_info.arquivo_xlsx)
                usr = exec_info.user

                with db.session.no_autoflush:
                    for adm in exec_info.license_usr.admins:
                        admins.append(adm.email)

                exec_data: dict[str, str | list[str]] = {
                    "pid": pid,
                    "display_name": display_name,
                    "xlsx": xlsx,
                    "username": str(usr.nome_usuario),
                    "email": str(usr.email),
                    "admins": admins,
                }

                if exec_info.scheduled_execution:
                    email_notify = str(exec_info.scheduled_execution[-1].email)
                    task_name = str(exec_info.scheduled_execution[-1].name)
                    exec_data.update({
                        "email_notify": email_notify,
                        "task_name": task_name,
                    })

                db.session.commit()
                db.session.close()

                return exec_data

            if not task_id:
                raise Exception("Execution not found!")

            return exec_info

        except Exception as e:
            app.logger.exception("An error occurred: %s", str(e))
            return {"message": "An internal error has occurred!"}, 500


__all__ = [
    makezip,
    enviar_arquivo_para_gcs,
    load_cache,
    format_message_log,
    "generate_signed_url",
]
