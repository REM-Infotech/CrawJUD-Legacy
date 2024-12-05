import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

from app import create_test_app


@pytest.fixture
def app():
    """Cria uma instância do aplicativo Flask para testes."""
    app, _, db = create_test_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()  # Cria as tabelas necessárias para os testes
        yield app
        db.session.remove()


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def runner(app: Flask):
    return app.test_cli_runner()


@pytest.fixture()
def socketio_client(client: FlaskClient):
    _, io = create_test_app()
    socketio = io.test_client(app, flask_test_client=client)
    yield socketio
    socketio.disconnect()


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
