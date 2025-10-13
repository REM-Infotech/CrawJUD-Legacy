"""Módulo de controle de controle da model execuções dos bots."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db

if TYPE_CHECKING:
    from app.models import User


class Executions(db.Model):
    """Model de execuções dos bots."""

    __tablename__ = "executions"
    pid: str = Column(String(length=64), nullable=False)
    Id: int = Column("id", Integer, primary_key=True)
    status: str = Column("status", String(length=64), nullable=False)
    file_output: str = Column("file_output", String(length=512))
    total_rows: str = Column("total_rows", String(length=64))
    url_socket: str = Column("url_socket", String(length=64))
    data_execucao: datetime = Column(
        "data_execucao",
        db.DateTime,
        default=lambda: datetime.now(ZoneInfo("America/Manaus")),
    )
    data_finalizacao: datetime = Column(
        "data_finalizacao",
        db.DateTime,
        default=lambda: datetime.now(ZoneInfo("America/Manaus")),
    )
    arquivo_xlsx: str = Column("arquivo_xlsx", String(length=64))

    user_id: int = Column(Integer, db.ForeignKey("users.id"))
    User: Mapped[User] = db.relationship()
