import pytest
from flask import Flask
from flask.testing import FlaskClient

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
