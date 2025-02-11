"""Module: status.

This module manages the status of bots (Start and Stop).
"""

from __future__ import annotations

import asyncio
import json
import logging
import traceback
import unicodedata
from datetime import datetime
from os import path
from pathlib import Path
from typing import Self

import aiofiles
import openpyxl
import pytz
from flask_sqlalchemy import SQLAlchemy
from openpyxl.worksheet.worksheet import Worksheet
from quart import Quart
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .makefile import makezip
from .send_email import email_start, email_stop
from .server_side import FormatMessage, load_cache
from .upload_zip import enviar_arquivo_para_gcs

url_cache = []
logger = logging.getLogger(__name__)


class SetStatus:
    """A class to manage  the status of bots (Start and Stop)."""

    def __init__(self) -> None:
        """Initialize the class."""

    async def config(
        self,
        form: dict[str, str] = None,
        files: dict[str, FileStorage] = None,
        id: int = 0,  # noqa: A002
        system: str = None,
        typebot: str = None,
        usr: str = None,
        pid: str = None,
        status: str = "Finalizado",
        **kwargs: dict[str, any],
    ) -> Self:
        """Initialize the SetStatus instance.

        :param form: Dictionary containing form data.
        :param files: Dictionary containing file data.
        :param id: Bot ID.
        :param system: System name.
        :param typebot: type of bot.
        :param usr: User name.
        :param pid: Process ID.
        :param status: Status of the bot.
        """
        self.form = form
        if self.form is None:
            self.form = kwargs

        self.files = files
        self.id = id
        self.system = system
        self.typebot = typebot

        self.user = self.form.get("user", usr)
        self.pid = self.form.get("pid", pid)

        self.status = status

        return self

    async def format_string(self, string: str) -> str:
        """Format a string to be a secure filename.

        Args:
            string (str): The string to format.

        Returns:
                str: The formatted string.

        """
        return secure_filename(
            "".join([c for c in unicodedata.normalize("NFKD", string) if not unicodedata.combining(c)]),
        )

    async def start_bot(  # noqa: C901
        self,
        app: Quart,
        db: SQLAlchemy,
        user: str = None,
        pid: str = None,
        id: int = None,  # noqa: A002
    ) -> tuple[str, str]:
        """Start the bot and handle file uploads and database interactions.

        :param app: Quart application instance.
        :param db: SQLAlchemy database instance.
        :param user: User name.
        :param pid: Process ID.
        :param id: Bot ID.

        Returns:
            tuple containing the path to the arguments file and the bot display name.

        """
        from app.models import BotsCrawJUD, Executions, LicensesUsers, Users

        user = self.user if user is None else user
        pid = self.pid if pid is None else pid
        id = self.id if id is None else id  # noqa: A001

        path_pid = Path(__file__).cwd().joinpath(app.config["TEMP_PATH"]).joinpath(pid).resolve()
        path_pid.mkdir(parents=True, exist_ok=True)

        if self.files is not None:
            for f, value in self.files.items():
                if "xlsx" not in f:
                    f = await asyncio.create_task(self.format_string(f))

                filesav = path_pid.joinpath(f)
                await value.save(filesav)

        data = {}

        path_args = path.join(path_pid, f"{pid}.json")
        if self.form is not None:
            for key, value in self.form.items():
                data.update({key: value})

        data.update({"id": id, "system": self.system, "typebot": self.typebot})

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

        name_column = Executions.__table__.columns["arquivo_xlsx"]
        max_length = name_column.type.length
        xlsx_ = str(data.get("xlsx", "Sem Arquivo"))

        if len(data.get("xlsx", "Sem Arquivo")) > int(max_length):
            xlsx_ = xlsx_[: int(max_length)]

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
        bt = BotsCrawJUD.query.filter(BotsCrawJUD.id == id).first()
        license_ = LicensesUsers.query.filter(LicensesUsers.license_token == usr.licenseusr.license_token).first()

        execut.user = usr
        execut.bot = bt
        execut.license_usr = license_

        db.session.add(execut)
        db.session.commit()

        try:
            email_start(execut, app)

        except Exception:
            err = traceback.format_exc()
            logger.exception(err)

        return (path_args, bt.display_name)

    async def botstop(
        self,
        db: SQLAlchemy,
        app: Quart,
        pid: str = None,
        status: str = "Finalizado",
        system: str = None,
        typebot: str = None,
    ) -> str:
        """Stop the bot and handle file uploads and database interactions.

        :param db: SQLAlchemy database instance.
        :param app: Quart application instance.
        :param pid: Process ID.
        :param status: Status of the bot.
        :param system: System name.
        :param typebot: type of bot.

        Returns:
            The name of the object destination.

        """
        from app.models import Executions

        try:
            status = self.status if self.status != "Finalizado" else status
            pid = self.pid if pid is None else pid

            system = self.system if system is None else system
            typebot = self.typebot if typebot is None else typebot

            zip_file = makezip(pid)
            objeto_destino = path.basename(zip_file)
            enviar_arquivo_para_gcs(zip_file)

            execution = Executions.query.filter(Executions.pid == pid).first()

            try:
                email_stop(execution, app)
            except Exception as e:
                raise e

            execution.status = status
            execution.file_output = objeto_destino
            execution.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
            db.session.commit()
            db.session.close()
            return objeto_destino

        except Exception as e:
            raise e


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
