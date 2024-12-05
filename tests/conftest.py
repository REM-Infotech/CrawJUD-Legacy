import pytest
from flask import Flask
from werkzeug.datastructures import FileStorage

from app import AppTestFactory

factory = AppTestFactory()
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


@pytest.fixture()
def client(app: Flask):

    return app.test_client()


@pytest.fixture()
def runner(app: Flask):
    return app.test_cli_runner()


# @pytest.fixture()
# def socketio_client(client: FlaskClient):
#     _, io = create_test_app()
#     socketio = io.test_client(app, flask_test_client=client)
#     yield socketio
#     socketio.disconnect()


@pytest.fixture()
def args_bot():

    from os import path
    from pathlib import Path

    xls_Test = path.join(Path(__file__).parent.resolve(), "archives", "xls_.xlsx")
    basename = path.basename(xls_Test)
    with Path(xls_Test).open("rb") as f:

        data = {
            "url": "https://",
            "files": {basename: (basename, f)},
            "data": {
                "pid": "V2A5G1",
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
def args_statusbot():

    from os import path
    from pathlib import Path

    xls_Test = path.join(Path(__file__).parent.resolve(), "archives", "xls_.xlsx")
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
                "pid": "V2A5G1",
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

    from status import SetStatus

    setstatus = SetStatus(**args_statusbot)
    yield setstatus
