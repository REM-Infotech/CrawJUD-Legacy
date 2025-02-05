"""
Module: response_test.

This module contains tests for Flask API routes.

Functions:
    test_client_flask(client: FlaskClient, app: Flask, args_bot: dict[str, str | Any], create_dummy_pid):
        Tests various API routes and their responses.
    __doc__():
        Placeholder for module-level docstring.
"""

from typing import Any

from flask import Flask
from flask.testing import FlaskClient


def test_client_flask(client: FlaskClient, app: Flask, args_bot: dict[str, str | Any], create_dummy_pid):
    """
    Teste De Rotas API.

    Args:
        client (FlaskClient): Cliente de testes Flask
        app (Flask): App Flask
        args_bot (dict[str, str | Any]): Argumentos para o bot
        create_dummy_pid (fixture): Cria um PID de teste

    """
    user, pid = create_dummy_pid
    response_index = client.get("/")
    botstop_error = client.post(f"/stop/{user}/123456")
    botstop_success = client.post(f"/stop/{user}/{pid}")

    response_bot_error = client.post("/bot/1/projudi/capa")

    app.debug = True
    response_bot_sucess = client.post("/bot/1/projudi/capa", **{"data": args_bot})

    chk_index = response_index.status_code == 302
    chk_bot_error = response_bot_error.status_code == 500
    chk_bot_success = response_bot_sucess.status_code == 200

    chk_botstop_error = botstop_error.status_code == 404 or botstop_error.status_code == 500
    chk_botstop_success = botstop_success.status_code == 200

    assert all(  # nosec: B011
        [
            chk_index,
            chk_bot_error,
            chk_bot_success,
            chk_botstop_error,
            chk_botstop_success,
        ]
    )


print(test_client_flask.__doc__)
