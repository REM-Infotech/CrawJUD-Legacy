from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone
from werkzeug.datastructures import FileStorage

from app import create_test_app as factory

create_test_app = factory.create_app
create_db = factory.init_database
create_socket = factory.init_socket
create_mail = factory.init_mail
create_redis = factory.init_redis
create_routes = factory.init_routes


@pytest.fixture(scope="session")
def app():
    """Cria uma instância do aplicativo Flask para testes."""
    app = create_test_app()
    app.config["TESTING"] = True
    create_socket(app)
    create_db(app)
    create_redis(app)
    create_mail(app)
    create_routes(app)

    yield app

    with app.app_context():
        app.debug = False
        db: SQLAlchemy = app.extensions.get("sqlalchemy")
        db.drop_all()


@pytest.fixture()
def client(app: Flask):
    """Return Cliente Flask

    Args:
        app (Flask): App Flask

    Returns:
        FlaskClient: Cliente Flask
    """
    return app.test_client()


# @pytest.fixture()
# def runner(app: Flask):
#     return app.test_cli_runner()


# @pytest.fixture()
# def socketio_client(client: FlaskClient):
#     _, io = create_test_app()
#     socketio = io.test_client(app, flask_test_client=client)
#     yield socketio
#     socketio.disconnect()


@pytest.fixture()
def args_bot():
    """Argumentos Bot (Sem pós-formatação)

    Yields:
        dict: Argumentos de inicialização bots
    """
    from os import path
    from pathlib import Path

    from app.misc import generate_pid

    xls_Test = path.join(
        Path(__file__).parent.resolve(), "archives_for_test", "xls_.xlsx"
    )
    basename = path.basename(xls_Test)
    with Path(xls_Test).open("rb") as f:
        data = {
            "url": "https://",
            "files": {basename: (basename, f)},
            "data": {
                "pid": generate_pid(),
                "user": "test",
                "xlsx": basename,
                "username": "test",
                "password": "test",
                "login_method": "pw",
                "creds": "test",
                "state": "AM",
            },
        }

        yield data


@pytest.fixture()
def args_statusbot():
    """Argumentos de Bot com formatação pós POST

    Yields:
        dict: Dicionario com argumentos
    """

    from os import path
    from pathlib import Path

    from app.misc import generate_pid

    xls_Test = path.join(
        Path(__file__).parent.resolve(), "archives_for_test", "xls_.xlsx"
    )
    basename = path.basename(xls_Test)
    with Path(xls_Test).open("rb") as f:
        f = FileStorage(f, basename)
        data = {
            "id": 1,
            "status": "Em Execução",
            "system": "projudi",
            "typebot": "capa",
            "files": {basename: f},
            "form": {
                "pid": generate_pid(),
                "user": "robotz213",
                "xlsx": basename,
                "username": "test",
                "password": "test",
                "login_method": "pw",
                "creds": "test",
                "state": "AM",
            },
        }

        yield data


@pytest.fixture()
def SetStatus(args_statusbot: dict[str, str]):
    """Instância da classe "Setstatus"

    Args:
        args_statusbot (dict[str, str]): argumentos de inicialização com formatação "pós POST"

    Yields:
        SetStatus: Classe "SetStatus"
    """
    from status import SetStatus

    setstatus = SetStatus(**args_statusbot)
    yield setstatus


@pytest.fixture(scope="function")
def io(app: Flask, client: FlaskClient):
    """Cliente do SocketIO

    Args:
        app (Flask): Aplicação Flask
        client (FlaskClient): Cliente Flask

    Yields:
        SocketIOTestClient: Cliente Socketio
    """
    io: SocketIO = app.extensions["socketio"]
    socketio_client = SocketIOTestClient(app, io, flask_test_client=client)
    socketio_client.connect("/log")
    yield socketio_client
    socketio_client.disconnect()


@pytest.fixture(scope="function")
def create_dummy_pid(app: Flask, args_bot: dict[str, str | Any]):
    """
    Instânciamento de Usuário, Licença e Execução "Dummy"
    Retorna Usuario e PID para testes

    Args:
        app (Flask): App flask
        args_bot (dict[str, str  |  Any]): argumentos bots

    Yields:
        user, pid (tuple[str, str]): Usuário e PID criados
    """
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
                Path(__file__)
                .cwd()
                .resolve()
                .joinpath("configs")
                .joinpath("export.xlsx")
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
