"""Module for testing the CrawJUD-Bots functionalities."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from bot import WorkerBot
from status import SetStatus as st_stt


class TestRunner:
    """Class containing test cases for CrawJUD-Bots."""

    def test_status_start(self, app: Flask, SetStatus: st_stt, create_dummy_pid):
        """
        Test the start status of the bot.

        Args:
            app (Flask): The Flask application instance.
            SetStatus (st_stt): The status setter.
            create_dummy_pid: Fixture for creating dummy PID.

        """
        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        with app.app_context():
            path_args, display_name = SetStatus.start_bot(app, db, user, pid, 1)

            worker_thread = WorkerBot(
                path_args=path_args,
                display_name=display_name,
                system="projudi",
                typebot="capa",
            )
            is_started = worker_thread.start(app, db)

            check_result = any([is_started == 500, is_started == 200])

            assert check_result

    def test_status_stop(self, app: Flask, SetStatus: st_stt, create_dummy_pid):
        """
        Test the stop status of the bot.

        Args:
            app (Flask): The Flask application instance.
            SetStatus (st_stt): The status setter.
            create_dummy_pid: Fixture for creating dummy PID.

        """
        from utils import get_file

        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        user = str(user)
        pid = str(pid)

        with app.app_context():
            stop = SetStatus.botstop(db, app, pid)
            check_return = WorkerBot().stop(12345, pid, app)

            file_ = get_file(pid, app)

        checks = [
            isinstance(check_return, str),
            isinstance(stop, str),
            isinstance(file_, str),
        ]
        assert checks

    def test_status_stop_esaj(self, app: Flask, SetStatus: st_stt, create_dummy_pid):
        """
        Test the stop status of the bot for ESAJ system.

        Args:
            app (Flask): The Flask application instance.
            SetStatus (st_stt): The status setter.
            create_dummy_pid: Fixture for creating dummy PID.

        """
        user, pid = create_dummy_pid
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        user = str(user)
        pid = str(pid)

        with app.app_context():
            stop = SetStatus.botstop(db, app, pid, "esaj", "protocolo")
            check_return = WorkerBot().stop(12345, pid, app)
            assert check_return is not None and stop is not None
