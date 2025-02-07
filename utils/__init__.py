"""Miscellaneous utilities and helpers for the CrawJUD-Bots application."""

import importlib  # noqa: F401
from datetime import datetime  # noqa: F401

from dotenv_vault import load_dotenv

import utils.bots_logs  # noqa: F401

from .check_cors import check_allowed_origin
from .get_location import GeoLoc
from .git_py import _release_tag, check_latest, checkout_release, update_servers
from .make_celery import make_celery

signed_url_lifetime = 300
__all__ = [
    "_release_tag",
    "check_latest",
    "checkout_release",
    "update_servers",
    "GeoLoc",
    "check_allowed_origin",
    "make_celery",
    utils.bots_logs.init_log,
    utils.bots_logs.asyncinit_log,
]

load_dotenv()


# def stop_execution(app: Flask, pid: str, robot_stop: bool = False) -> tuple[dict[str, str], int]:
#     """Stop the execution of a bot based on its PID.

#     Args:
#         app (Flask): The Flask application instance.
#         pid (str): The process identifier of the bot.
#         robot_stop (bool, optional): Flag to indicate robot stop. Defaults to False.

#     Returns:
#         tuple[dict[str, str], int]: A message and HTTP status code.

#     """
#     from app import db
#     from app.models import Executions, ThreadBots
#     from status import SetStatus

#     try:
#         processID = ThreadBots.query.filter(ThreadBots.pid == pid).first()  # noqa: N806

#         if processID:
#             get_info = db.session.query(Executions).filter(Executions.pid == pid).first()

#             system = get_info.bot.system
#             typebot = get_info.bot.type
#             user = get_info.user.login
#             get_info.status = "Finalizado"
#             get_info.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
#             filename = get_file(pid, app)

#             if filename != "":
#                 get_info.file_output = filename
#                 db.session.commit()
#                 db.session.close()

#             elif filename == "":
#                 get_info.file_output = SetStatus(usr=user, pid=pid, system=system, typebot=typebot).botstop(db, app)
#                 db.session.commit()
#                 db.session.close()

#         elif not processID:
#             raise Exception("Execution not found!")

#         return {"message": "bot stopped!"}, 200

#     except Exception as e:
#         app.logger.error("An error occurred: %s", str(e))
#         return {"message": "An internal error has occurred!"}, 500
