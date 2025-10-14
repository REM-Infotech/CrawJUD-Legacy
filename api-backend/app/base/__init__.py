"""Bases customizadas para classes de Extensões e Modelos."""

from ._sqlalchemy._model import Model
from ._sqlalchemy._query import Query

__all__ = ["Model", "Query"]
