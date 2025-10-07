from contextlib import suppress
from typing import ClassVar, Self, cast

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.sql.elements import KeyedColumnElement

from app._types import MyAny

from ._query import Query, QueryProperty


class FSAProperty:
    fsa_instante: SQLAlchemy = SQLAlchemy()

    def __set__(self, *args, **kwargs) -> None:
        self.fsa_instante = args[1]

    def __get__(self, *args, **kwargs) -> SQLAlchemy:
        with suppress(KeyError):
            from app import app

            with app.app_context():
                if "sqlalchemy" in app.extensions:
                    db: SQLAlchemy = app.extensions["sqlalchemy"]
                    self.fsa_instante = db

        return self.fsa_instante


class Model(MappedAsDataclass, DeclarativeBase):
    query: ClassVar[Query[Self]] = cast(Query[Self], QueryProperty())

    __fsa__: ClassVar[SQLAlchemy] = cast(SQLAlchemy, FSAProperty())

    def __init_subclass__(cls, **kw: MyAny) -> None:
        def camel_to_snake(name: str) -> str:
            import re

            s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
            return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        snake_cased = camel_to_snake(cls.__class__.__name__)
        cls.__name__ = cls.__tablename__ or snake_cased

        super().__init_subclass__(**kw)

    @classmethod
    def get_column_statement(cls) -> list[KeyedColumnElement[Self]]:
        if not hasattr(cls, "__table__"):
            return []

        return list(cls.__table__.columns)
