"""Modulo de controle da model bots."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String

from app.resources.extensions import db

if TYPE_CHECKING:
    from app.models import LicenseUser as LicenseUser
    from app.models import User as User
now_ = datetime.now(ZoneInfo("America/Manaus"))


class Bots(db.Model):
    """Bots Model."""

    __tablename__ = "bots"
    Id: int = Column("id", Integer, primary_key=True)
    display_name: str = Column(
        "display_name",
        String(length=64),
        nullable=False,
    )
    system: str = Column("system", String(length=64), nullable=False)
    type: str = Column("type", String(length=64), nullable=False)
    form_cfg: str = Column("form_cfg", String(length=64), nullable=False)
    classification: str = Column(
        "classification",
        String(length=64),
        nullable=False,
    )
    text: str = Column("text", String(length=512), nullable=False)
