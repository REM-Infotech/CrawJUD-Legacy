"""Modulo de controle da model bots."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String

from app.resources.extensions import db


class Bots(db.Model):
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
