"""Module to handle application error reporting via email using SMTPHandler."""

import logging
from logging.handlers import SMTPHandler
from os import environ

from dotenv_vault import load_dotenv

from web import app

load_dotenv()
values = environ

MAIL_USERNAME = values["MAIL_USERNAME"]
MAIL_PASSWORD = values["MAIL_PASSWORD"]

mail_handler = SMTPHandler(
    mailhost=values["MAIL_SERVER"],
    fromaddr=values["MAIL_DEFAULT_SENDER"],
    toaddrs=["adm@fmvadv.com.br"],
    subject="Application Error",
    credentials=(MAIL_USERNAME, MAIL_PASSWORD),
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))

if not app.debug:
    app.logger.addHandler(mail_handler)
