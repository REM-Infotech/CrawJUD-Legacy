import json
import unicodedata
from datetime import datetime
from os import path
from pathlib import Path
from typing import Dict

import openpyxl
import pytz
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from openpyxl.worksheet.worksheet import Worksheet
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .makefile import makezip
from .send_email import email_start, email_stop
from .upload_zip import enviar_arquivo_para_gcs

url_cache = []


class SetStatus:
    def __init__(
        self,
        form: Dict[str, str] = {},
        files: Dict[str, FileStorage] = {},
        id: int = 0,
        system: str = None,
        typebot: str = None,
        usr: str = None,
        pid: str = None,
        status: str = "Finalizado",
        **kwargs,
    ) -> str:
        self.form = form
        self.files = files
        self.id = id
        self.system = system
        self.typebot = typebot
        self.user = form.get("user", usr)
        self.pid = form.get("pid", pid)
        self.status = status

    def format_String(self, string: str) -> str:
        return secure_filename(
            "".join(
                [
                    c
                    for c in unicodedata.normalize("NFKD", string)
                    if not unicodedata.combining(c)
                ]
            )
        )

    def start_bot(
        self,
        app: Flask,
        db: SQLAlchemy,
        user: str = None,
        pid: str = None,
        id: int = None,
    ) -> tuple[str, str]:
        from app.models import BotsCrawJUD, Executions, LicensesUsers, Users

        user = self.user if user is None else user
        pid = self.pid if pid is None else pid
        id = self.id if id is None else id

        path_pid = Path(path.join(Path(__file__).cwd(), "exec", pid))
        path_pid.mkdir(parents=True, exist_ok=True)

        if self.files:
            for f, value in self.files.items():
                if "xlsx" not in f or app.testing is True:
                    f = self.format_String(f)

                filesav = path.join(path_pid, f)
                value.save(filesav)

        data = {}

        path_args = path.join(path_pid, f"{pid}.json")
        if self.form:
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
            data_inicio_formated = datetime.strptime(
                data.get("data_inicio"), "%Y-%m-%d"
            )

            data_fim_formated = datetime.strptime(data.get("data_fim"), "%Y-%m-%d")

            diff = data_fim_formated - data_inicio_formated
            rows = diff.days + 2

        elif data.get("typebot") == "proc_parte":
            rows = len(list(data.get("varas"))) + 1

        data.update({"total_rows": rows})

        with open(path_args, "w") as f:
            f.write(json.dumps(data))

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
        license_ = LicensesUsers.query.filter(
            LicensesUsers.license_token == usr.licenseusr.license_token
        ).first()

        execut.user = usr
        execut.bot = bt
        execut.license_usr = license_

        db.session.add(execut)
        db.session.commit()

        try:
            email_start(execut, app)

        except Exception as e:  # pragma: no cover
            print(e)

        return (path_args, bt.display_name)

    def botstop(
        self,
        db: SQLAlchemy,
        app: Flask,
        pid: str = None,
        status: str = "Finalizado",
        system: str = None,
        typebot: str = None,
    ) -> str:
        from app.models import Executions

        try:
            status = self.status if self.status != "Finalizado" else status
            pid = self.pid if pid is None else pid

            system = self.system if system is None else system
            typebot = self.typebot if typebot is None else typebot

            # chk_srv = platform.system() == "Windows"
            # chk_sys = system.lower() == "esaj"
            # chk_typebot = typebot.lower() == "protocolo"

            # if all([chk_srv, chk_sys, chk_typebot]):

            #     json_args = path.join(
            #         pathlib.Path(__file__).cwd(), "exec", pid, f"{pid}.json"
            #     )
            #     with open(json_args, "rb") as f:
            #         arg = json.load(f)["login"]

            #     try:
            #         self.uninstall(arg)
            #     except Exception as e:
            #         print(e)

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
