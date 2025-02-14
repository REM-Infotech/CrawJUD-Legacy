"""Initialization of database models for the CrawJUD-Bots application."""

from .bots import BotsCrawJUD, CacheLogs, Credentials, Executions, ThreadBots
from .schedule import CrontabModel, ScheduleModel
from .secondaries import admins, execution_bots
from .srv import Servers
from .users import LicensesUsers, Users

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
    ScheduleModel,
    CrontabModel,
]
