"""Módulo do Modelo License."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import MappedAsDataclass

from app.resources.extensions import db


class License(db.Model, MappedAsDataclass):
    """Modelo User."""

    __tablename__ = "licenses"
    Id = Column("id", Integer, primary_key=True, nullable=False, unique=True)
    Name = Column("name", String(128), nullable=False)
    Description = Column("description", String(256), nullable=False)
