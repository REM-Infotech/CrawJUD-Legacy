from contextlib import suppress
from typing import ClassVar, Self, cast

from __types import MyAny
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model as FSA_Model

from app.resources import camel_to_snake

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


class FSATableName:
    _tablename: ClassVar[str] = ""

    def __set__(self, *args) -> None:
        self._tablename = args[1]  # pyright: ignore[reportAttributeAccessIssue]

    def __get__(
        self,
        cls: Model | None = None,
        *args: MyAny,
        **kwargs: MyAny,
    ) -> str:
        if cls:
            snake_cased = camel_to_snake(cls.__class__.__name__)
            cls.__name__ = cls.__tablename__ or snake_cased  # pyright: ignore[reportAttributeAccessIssue]

        return self._tablename


class Model(FSA_Model):
    query: ClassVar[Query[Self]] = cast(Query[Self], QueryProperty())  # pyright: ignore[reportIncompatibleVariableOverride]
    __fsa__: ClassVar[SQLAlchemy] = cast(SQLAlchemy, FSAProperty())
    __tablename__: ClassVar[str] = FSAProperty()
