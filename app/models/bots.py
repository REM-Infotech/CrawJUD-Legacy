"""Defines database models for CrawJUD bots and their execution details.

Provides structures for bot configurations, credentials, and execution logging.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db

from .users import LicensesUsers

if TYPE_CHECKING:
    from collections.abc import Buffer

now_ = datetime.now(ZoneInfo("America/Manaus"))


class BotsCrawJUD(db.Model):
    """Represents a CrawJUD bot entity.

    Attributes:
        id (int): Primary key for the bot.
        display_name (str): Display name of the bot.
        system (str): System type or identifier.
        state (str): Operational status of the bot.
        client (str): Client identifier.
        type (str): Type classification of the bot.
        form_cfg (str): Configuration form reference.
        classification (str): Classification of the bot's purpose.
        text (str): Descriptive text or notes.

    """

    __tablename__ = "bots"
    id: int = Column(Integer, primary_key=True)
    display_name: str = Column(String(length=64), nullable=False)
    system: str = Column(String(length=64), nullable=False)
    state: str = Column(String(length=64), nullable=False)
    client: str = Column(String(length=64), nullable=False)
    type: str = Column(String(length=64), nullable=False)
    form_cfg: str = Column(String(length=64), nullable=False)
    classification: str = Column(String(length=64), nullable=False)
    text: str = Column(String(length=512), nullable=False)


class Credentials(db.Model):
    """Represents stored credentials for a user or system.

    Attributes:
        id (int): Primary key for the credential.
        nome_credencial (str): Descriptive name for the credential.
        system (str): System type or identifier.
        login_method (str): Authentication method used.
        login (str): Username or login identifier.
        password (str): Password stored for the credential.
        key (str): Optional key used in authentication.
        certficate (str): Optional certificate name.
        certficate_blob (bytes): Binary certificate data.
        license_id (int): Foreign key referencing the license.

    """

    __tablename__ = "credentials"
    id: int = Column(Integer, primary_key=True)
    nome_credencial: str = Column(String(length=64), nullable=False)
    system: str = Column(String(length=64), nullable=False)
    login_method: str = Column(String(length=64), nullable=False)
    login: str = Column(String(length=64), nullable=False)
    password: str = Column(String(length=64))
    key: str = Column(String(length=64))
    certficate: str = Column(String(length=64))
    certficate_blob: Buffer = Column(db.LargeBinary(length=(2**32) - 1))

    license_id: int = Column(Integer, db.ForeignKey("licenses_users.id"))
    license_usr: Mapped[LicensesUsers] = db.relationship()


class Executions(db.Model):
    """Represents bot execution records.

    Attributes:
        pid (str): Process identifier for the execution.
        id (int): Primary key for the execution record.
        status (str): Current status of the execution.
        file_output (str): Path or reference to output file.
        total_rows (str): Row count for processed data.
        url_socket (str): Socket address for communication.
        data_execucao (datetime): Execution start timestamp.
        data_finalizacao (datetime): Execution end timestamp.
        arquivo_xlsx (str): Reference to the exported .xlsx file.
        bot_id (int): Foreign key referencing the bot.
        user_id (int): Foreign key referencing the user.
        license_id (int): Foreign key referencing the license.

    """

    __tablename__ = "executions"
    pid: str = Column(String(length=64), nullable=False)
    id: int = Column(Integer, primary_key=True)
    status: str = Column(String(length=64), nullable=False)
    file_output: str = Column(String(length=512))
    total_rows: str = Column(String(length=64))
    url_socket: str = Column(String(length=64))
    data_execucao: datetime = Column(db.DateTime, default=now_)
    data_finalizacao: datetime = Column(db.DateTime, default=now_)
    arquivo_xlsx: str = Column(String(length=64))
