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
    id: int = Column(Integer, primary_key=True)
    display_name: str = Column(String(length=64), nullable=False)
    system: str = Column(String(length=64), nullable=False)
    type: str = Column(String(length=64), nullable=False)
    form_cfg: str = Column(String(length=64), nullable=False)
    classification: str = Column(String(length=64), nullable=False)
    text: str = Column(String(length=512), nullable=False)
