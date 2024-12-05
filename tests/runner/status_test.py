from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from status import SetStatus as st_std


def test_startbot(app: Flask, SetStatus: st_std):

    db: SQLAlchemy = app.extensions["sqlalchemy"]
    with app.app_context():

        start = SetStatus.start_bot(app, db)
        check_return = type(start) is tuple
        assert check_return
