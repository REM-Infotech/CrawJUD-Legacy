import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

from status import SetStatus as st_stt


class TestCrawJUD:

    @pytest.fixture(scope="function")
    def create_dummy_pid(self, app: Flask, args_bot: dict[str, str | Any]):

        import random
        import string

        from app.models import BotsCrawJUD, Executions, LicensesUsers, ThreadBots

        digits = random.sample(string.digits, 6)
        process_id = int("".join(digits))

        data: dict[str, str | dict[str, str]] | None = args_bot.get("data")

        user = data.get("username", None)
        pid = data.get("pid", None)

        db: SQLAlchemy = app.extensions["sqlalchemy"]

        with app.app_context():

            db.drop_all()
            db.create_all()

            def _user_license():

                from app.models import LicensesUsers, Users

                license_dummy = str(uuid4())

                usr = Users(login=user, nome_usuario=user, email="example@example.com")
                usr.senhacrip = "test"

                license_user = LicensesUsers(
                    name_client="dummy",
                    cpf_cnpj="12345678987654",
                    license_token=license_dummy,
                )

                usr.licenseusr = license_user

                return usr, license_user

            def _bots(license_user: LicensesUsers):

                df = pd.read_excel(
                    os.path.join(Path(__file__).cwd(), "configs", "export.xlsx")
                )
                df.columns = df.columns.str.lower()
                bot_info = None
                data = []
                for values in list(df.to_dict(orient="records")):

                    key = list(values)[1]
                    value = values.get(key)

                    chk_bot = BotsCrawJUD.query.filter_by(**{key: value}).first()

                    if not chk_bot:
                        appends = BotsCrawJUD()

                        for key, var in values.items():
                            appends.__dict__.update({key: var})

                        license_user.bots.append(appends)

                        if (
                            appends.system.lower() == "projudi"
                            and appends.type.lower() == "capa"
                        ):
                            bot_info = appends

                        data.append(appends)

                db.session.add_all(data)

                return license_user, bot_info

            def _execut(usr, license_, bot_info):

                rows = process_id
                bt = bot_info
                process = ThreadBots(pid=pid, processID=process_id)
                execut = Executions(
                    pid=pid,
                    status="Em Execução",
                    arquivo_xlsx="xls_.xlsx",
                    url_socket=data.get("url_socket"),
                    total_rows=rows,
                    data_execucao=datetime.now(timezone("America/Manaus")),
                    file_output="Arguardando Arquivo",
                )

                execut.user = usr
                execut.bot = bt
                execut.license_usr = license_

                return execut, process

            usr, license_user = _user_license()
            license_user, bot_info = _bots(license_user)
            process, execut = _execut(usr, license_user, bot_info)

            db.session.add_all([process, execut, usr, license_user])
            db.session.commit()

        yield user, pid

        with app.app_context():
            db.drop_all()

    def test_route_start(
        self, client, args_bot: dict[str, str | Any], create_dummy_pid
    ):

        response = client.post("/bot/1/projudi/capa", **{"data": args_bot})
        assert response.status_code == 200

    def test_route_stop(self, client: FlaskClient, create_dummy_pid):

        user, pid = create_dummy_pid

        response = client.post(f"/stop/{user}/{pid}")
        assert response.status_code == 200

    def test_status_start(self, app: Flask, SetStatus: st_stt, create_dummy_pid):

        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        with app.app_context():

            start = SetStatus.start_bot(app, db, user, pid, 1)
            check_return = type(start) is tuple
            assert check_return

    def test_status_stop(self, app: Flask, SetStatus: st_stt, create_dummy_pid):

        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        with app.app_context():

            stop = SetStatus.botstop(db, app, pid)
            check_return = stop is not None
            assert check_return
