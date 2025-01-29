from datetime import datetime

import pytz

from app import db


class BotsCrawJUD(db.Model):
    __tablename__ = "bots"
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(length=45), nullable=False)
    system = db.Column(db.String(length=45), nullable=False)
    state = db.Column(db.String(length=45), nullable=False)
    client = db.Column(db.String(length=45), nullable=False)
    type = db.Column(db.String(length=45), nullable=False)
    form_cfg = db.Column(db.String(length=45), nullable=False)
    classification = db.Column(db.String(length=45), nullable=False)
    text = db.Column(db.String(length=512), nullable=False)


class Credentials(db.Model):
    __tablename__ = "credentials"
    id = db.Column(db.Integer, primary_key=True)
    nome_credencial = db.Column(db.String(length=45), nullable=False)
    system = db.Column(db.String(length=45), nullable=False)
    login_method = db.Column(db.String(length=45), nullable=False)
    login = db.Column(db.String(length=45), nullable=False)
    password = db.Column(db.String(length=45))
    key = db.Column(db.String(length=45))
    certficate = db.Column(db.String(length=45))
    certficate_blob = db.Column(db.LargeBinary(length=(2**32) - 1))

    license_id = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    license_usr = db.relationship(
        "LicensesUsers", backref=db.backref("credentials", lazy=True)
    )


class Executions(db.Model):
    __tablename__ = "executions"
    pid = db.Column(db.String(length=12), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(length=45), nullable=False)
    file_output = db.Column(db.String(length=512))
    total_rows = db.Column(db.String(length=45))
    url_socket = db.Column(db.String(length=64))
    data_execucao = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("America/Manaus"))
    )
    data_finalizacao = db.Column(
        db.DateTime, default=datetime.now(pytz.timezone("America/Manaus"))
    )
    arquivo_xlsx = db.Column(db.String(length=64))

    bot_id = db.Column(db.Integer, db.ForeignKey("bots.id"))
    bot = db.relationship("BotsCrawJUD", backref=db.backref("executions", lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("Users", backref=db.backref("executions", lazy=True))

    license_id = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    license_usr = db.relationship(
        "LicensesUsers", backref=db.backref("executions", lazy=True)
    )


class CacheLogs(db.Model):
    __bind_key__ = "cachelogs"
    __tablename__ = "cachelogs"
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(length=12), nullable=False)
    pos = db.Column(db.Integer, nullable=False)

    total = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Integer, nullable=False)
    errors = db.Column(db.Integer, nullable=False)
    remaining = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(length=45), nullable=False)

    last_log = db.Column(db.Text, nullable=False)


class ThreadBots(db.Model):
    __bind_key__ = "cachelogs"
    __tablename__ = "thread_bots"
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(length=12), nullable=False)
    processID = db.Column(db.String(length=64), nullable=False)
