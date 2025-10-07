"""Módulo do Modelo User."""

from dataclasses import dataclass

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db

from .license import License


@dataclass(init=False)
class User(db.Model):
    """Modelo User."""

    __tablename__ = "users"

    Id: int = Column(
        "id",
        Integer,
        primary_key=True,
        nullable=False,
        unique=True,
    )
    UserName: int = Column("username", String(128), nullable=False)
    DisplayName: int = Column("display_name", String(128), nullable=False)
    Email: int = Column("email", String(64), nullable=False)

    License: Mapped[License] = db.relationship(
        License,
        backref="users",
        lazy=True,
    )
    license_id: int = Column(
        "license_id",
        Integer,
        db.ForeignKey("licenses.id"),
        nullable=False,
    )
