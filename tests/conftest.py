from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator
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
from status import SetStatus

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
def client(app: Flask) -> FlaskClient:
    """Create a test client for the given Flask application.

    Args:
        app (Flask): The Flask application instance.
    Returns:
        FlaskClient: A test client for the Flask application.
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
def args_bot() -> Generator[Dict[str, Any], Any, None]:
    """Generate and yield a dictionary containing test data for a bot.

    The function constructs a dictionary with URL, file, and data information
    required for testing a bot. It reads an Excel file from a specified path,
    generates a process ID (pid), and includes user credentials and other
    necessary data.

    Yields:
        dict: A dictionary containing the following keys:
            - "url" (str): The URL for the bot.
            - "files" (dict): A dictionary with the basename of the Excel file
              as the key and a tuple containing the basename and file object as
              the value.
            - "data" (dict): A dictionary containing:
                - "pid" (str): A generated process ID.
                - "user" (str): The username for the bot.
                - "xlsx" (str): The basename of the Excel file.
                - "username" (str): The username for login.
                - "password" (str): The password for login.
                - "login_method" (str): The login method (e.g., "pw").
                - "creds" (str): Credentials for the bot.
                - "state" (str): The state code (e.g., "AM").
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
def args_statusbot() -> Generator[Dict[str, Any], Any, None]:
    """Generate and yield a dictionary containing test data for a bot's status.

    This function creates a dictionary with various keys representing the status,
    system, type of bot, files, and form data required for testing a bot. It reads
    an Excel file from a predefined path and includes it in the dictionary. The
    function uses the `generate_pid` function to generate a unique process ID.

    Yields:
        dict: A dictionary containing test data for the bot's status.
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
def SetStatus(args_statusbot: dict[str, str]) -> Generator[SetStatus, Any, None]:
    """Set the status using the provided arguments.

    Args:
        args_statusbot (dict[str, str]): A dictionary containing status arguments.
    Yields:
        setstatus: An instance of SetStatus initialized with the provided arguments.
    """
    from status import SetStatus

    setstatus = SetStatus(**args_statusbot)
    yield setstatus


@pytest.fixture(scope="function")
def io(app: Flask, client: FlaskClient) -> Generator[SocketIOTestClient, Any, None]:
    """Fixture to provide a SocketIO test client for the Flask application.

    This fixture initializes a SocketIO test client, connects it to the
    specified namespace, and yields the client for use in tests. After the
    test is completed, the client is disconnected.

    Args:
        app (Flask): The Flask application instance.
        client (FlaskClient): The Flask test client instance.
    Yields:
        SocketIOTestClient: The SocketIO test client connected to the "/log" namespace.
    """
    io: SocketIO = app.extensions["socketio"]
    socketio_client = SocketIOTestClient(app, io, flask_test_client=client)
    socketio_client.connect("/log")
    yield socketio_client
    socketio_client.disconnect()


@pytest.fixture(scope="function")
def create_dummy_pid(
    app: Flask, args_bot: dict[str, str | Any]
) -> Generator[
    tuple[str | dict[str, str] | None, str | dict[str, str] | None], Any, None
]:
    """Create a dummy process ID and populate the database with test data.

    This function sets up a dummy process ID and populates the database with
    test data for users, licenses, bots, and executions. It is intended for

    use in testing environments.
    Args:
        app (Flask): The Flask application instance.
        args_bot (dict[str, str | Any]): A dictionary containing bot arguments.
            Expected keys:
                - "data" (dict[str, str]): A dictionary containing user data.
                    Expected keys:
                        - "username" (str): The username of the user.
                        - "pid" (str): The process ID.
    Yields:
        tuple: A tuple containing the username and process ID.
    Example:
        >>> with app.app_context():
        >>>     user, pid = next(create_dummy_pid(app, args_bot))
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
