"""Module for database initialization and model registration.

This module initializes the application's database by creating tables and seeding
initial data including users and bots. It also registers model classes for use with
the Quart application.
"""

from os import environ, path
from pathlib import Path
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from quart import Quart

from .bots import BotsCrawJUD, Credentials, Executions, ThreadBots
from .schedule import CrontabModel, ScheduleModel
from .secondaries import admins, execution_bots
from .users import LicensesUsers, SuperUser, Users

load_dotenv()
__all__ = [
    admins,
    execution_bots,
    Users,
    LicensesUsers,
    SuperUser,
    BotsCrawJUD,
    Credentials,
    Executions,
    ScheduleModel,
    CrontabModel,
    ThreadBots,
]


async def init_database(app: Quart, db: SQLAlchemy) -> str:
    """Initialize the database with default configuration and seed data.

    This function creates all necessary tables, reads environment variables,
    and populates the database with initial data including user and bots records.

    Args:
        app (Quart): The Quart application instance.
        db (SQLAlchemy): The database instance.

    Returns:
        bool: True if the database initialization is successful.

    Raises:
        Exception: Propagates any exception raised during the database initialization.

    """
    try:
        values = environ
        if environ.get("STAGING"):
            db.drop_all()

        db.create_all()

        loginsys = values.get("LOGINSYS")
        nomeusr = values.get("NOMEUSR")
        emailusr = values.get("EMAILUSR")
        passwd = values.get("PASSUSR")

        dbase = Users.query.filter(Users.login == loginsys).first()
        if not dbase:
            user = Users(login=loginsys, nome_usuario=nomeusr, email=emailusr)
            user.senhacrip = passwd

            license_user = LicensesUsers.query.filter(LicensesUsers.name_client == "Robotz Dev").first()

            if not license_user:
                license_user = LicensesUsers(
                    name_client="Robotz Dev",
                    cpf_cnpj="55607848000175",
                    license_token=str(uuid4()),
                )

            user.licenseusr = license_user
            license_user.admins.append(user)
            super_user = SuperUser()

            super_user.users = user

            df = pd.read_excel(path.join(Path(__file__).parent.resolve(), "export.xlsx"))
            df.columns = df.columns.str.lower()

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
                    data.append(appends)

            db.session.add(user)
            db.session.add_all(data)
            db.session.add(license_user)
            db.session.commit()

            return True

    except Exception as e:
        raise e
