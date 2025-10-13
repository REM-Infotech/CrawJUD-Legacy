"""Módulo de controle de controle da model credenciais_robo."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db

if TYPE_CHECKING:
    from app.models import LicenseUser


now_ = datetime.now(ZoneInfo("America/Manaus"))


class CredenciaisRobo(db.Model):
    """Credenciais Robo Model."""

    __tablename__ = "credenciais_robo"
    id: int = Column(Integer, primary_key=True)
    nome_credencial: str = Column(String(length=64), nullable=False)
    system: str = Column(String(length=64), nullable=False)
    login: str = Column(String(length=64), nullable=False)
    password: str = Column(String(length=64))

    license_id: int = Column(Integer, db.ForeignKey("licenses_users.id"))
    license_usr: Mapped[LicenseUser] = db.relationship()
