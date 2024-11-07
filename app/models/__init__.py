from app import app, db

from app.models.srv import Servers

import platform

from dotenv import dotenv_values
from app.models.secondaries import admins, execution_bots
from app.models.users import Users, LicensesUsers
from app.models.bots import BotsCrawJUD, Credentials, Executions, CacheLogs, ThreadBots

__all__ = [
    admins,
    execution_bots,
    Users,
    LicensesUsers,
    BotsCrawJUD,
    Credentials,
    Executions,
    CacheLogs,
    ThreadBots,
    Servers,
]


class init_database:

    def __call__(self):

        values = dotenv_values()
        with app.app_context():

            db.create_all()

            NAMESERVER = values.get("NAMESERVER")
            HOST = values.get("HOSTNAME")

            if not Servers.query.filter(Servers.name == NAMESERVER).first():

                server = Servers(
                    name=NAMESERVER, address=HOST, system=platform.system()
                )
                db.session.add(server)
                db.session.commit()
