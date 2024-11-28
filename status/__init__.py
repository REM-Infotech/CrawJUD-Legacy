import json
import logging
import os
import pathlib
import platform
import unicodedata
from datetime import datetime

import openpyxl
import pytz
from openpyxl.worksheet.worksheet import Worksheet
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import app, db

from .makefile import makezip
from .send_email import email_start, email_stop
from .upload_zip import enviar_arquivo_para_gcs

url_cache = []


class SetStatus:

    def __init__(
        self,
        form: dict[str, str] = {},
        files: dict[str, FileStorage] = {},
        id: int = 0,
        system: str = None,
        typebot: str = None,
        usr: str = None,
        pid: str = None,
        status: str = "Finalizado",
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

    def start_bot(self) -> tuple[str, str]:

        from app.models import BotsCrawJUD, Executions, LicensesUsers, Users

        path_pid = os.path.join(app.config["TEMP_PATH"], self.pid)
        os.makedirs(path_pid, exist_ok=True)

        if self.files:
            for f, value in self.files.items():

                if "xlsx" not in f:
                    f = self.format_String(f)

                filesav = os.path.join(path_pid, f)
                value.save(filesav)

        data = {}
        path_args = os.path.join(path_pid, f"{self.pid}.json")
        if self.form:
            for key, value in self.form.items():
                data.update({key: value})

        data.update({"id": self.id, "system": self.system, "typebot": self.typebot})

        if data.get("xlsx"):
            input_file = os.path.join(
                pathlib.Path(path_args).parent.resolve(), data["xlsx"]
            )
            if os.path.exists(input_file):
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
            pid=self.pid,
            status="Em Execução",
            arquivo_xlsx=xlsx_,
            url_socket=data.get("url_socket"),
            total_rows=rows,
            data_execucao=datetime.now(pytz.timezone("America/Manaus")),
            file_output="Arguardando Arquivo",
        )

        usr = Users.query.filter(Users.login == self.user).first()
        bt = BotsCrawJUD.query.filter(BotsCrawJUD.id == self.id).first()
        license_ = LicensesUsers.query.filter(
            LicensesUsers.license_token == usr.licenseusr.license_token
        ).first()

        execut.user = usr
        execut.bot = bt
        execut.license_usr = license_

        db.session.add(execut)
        db.session.commit()

        try:
            email_start(execut)

        except Exception as e:
            logging.error(f"Exception: {e}", exc_info=True)

        return (path_args, bt.display_name)

    def botstop(self) -> str:
        from app.models import Executions

        try:
            srv = platform.system() in ("Windows")
            sys = self.system.lower() in ("esaj")
            typebot = self.typebot.lower() in ("protocolo")

            if all([srv, sys, typebot]):

                json_args = os.path.join(
                    os.getcwd(), "Temp", self.pid, f"{self.pid}.json"
                )
                with open(json_args, "rb") as f:
                    arg = json.load(f)["login"]

                try:
                    self.uninstall(arg)
                except Exception as e:
                    print(e)

            zip_file = makezip(self.pid)
            objeto_destino = os.path.basename(zip_file)
            enviar_arquivo_para_gcs(zip_file)

            execution = Executions.query.filter(Executions.pid == self.pid).first()

            try:
                email_stop(execution)
            except Exception as e:
                logging.error(f"Exception: {e}", exc_info=True)

            execution.status = self.status
            execution.file_output = objeto_destino
            execution.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
            db.session.commit()
            db.session.close()
            return objeto_destino

        except Exception as e:
            logging.error(f"Exception: {e}", exc_info=True)
