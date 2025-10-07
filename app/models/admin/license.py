"""Módulo do Modelo License."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.base import Model


class License(Model):
    """Modelo License."""

    __tablename__ = "licenses"
    Id: Mapped[int] = Column(
        "id",
        Integer,
        primary_key=True,
        nullable=False,
        unique=True,
    )
    Name: Mapped[str] = Column("name", String(128), nullable=False)
    Description: Mapped[str] = Column(
        "description",
        String(256),
        nullable=False,
    )
