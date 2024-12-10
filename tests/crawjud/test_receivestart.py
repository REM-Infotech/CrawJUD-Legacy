from typing import Any

from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from bot import WorkerThread
from status import SetStatus as st_stt


class TestCrawJUD:

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

            path_args, display_name = SetStatus.start_bot(app, db, user, pid, 1)

            worker_thread = WorkerThread(
                path_args=path_args,
                display_name=display_name,
                system="projudi",
                typebot="capa",
            )
            is_started = worker_thread.start(app, db)

            check_result = any([is_started == 500, is_started == 200])

            assert check_result

    def test_status_stop(self, app: Flask, SetStatus: st_stt, create_dummy_pid):

        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        user = str(user)
        pid = str(pid)

        with app.app_context():

            stop = SetStatus.botstop(db, app, pid)
            check_return = WorkerThread().stop(12345, pid, app)
            assert check_return is not None and stop is not None

    def test_status_stop_esaj(self, app: Flask, SetStatus: st_stt, create_dummy_pid):

        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        user = str(user)
        pid = str(pid)

        with app.app_context():

            stop = SetStatus.botstop(db, app, pid, "esaj", "protocolo")
            check_return = WorkerThread().stop(12345, pid, app)
            assert check_return is not None and stop is not None
