"""Módulo de tipos do task manager."""

from datetime import datetime, timedelta
from os import PathLike
from typing import Any, Literal, ParamSpec, TypeVar

from .bot import MessageLog, MessageType

type AnyType = Any

P = ParamSpec("P", bound=Any)
T = TypeVar("T", bound=AnyType)


type MethodsSearch = Literal["peticionamento", "consulta"]
type PolosProcessuais = Literal["Passivo", "Ativo"]
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes
type Dict = dict[str, PyStrings | PyNumbers]
type ListDict = list[Dict]
type ListPartes = list[tuple[ListDict], list[ListDict]]
type StatusBot = Literal["Inicializando", "Em Execução", "Finalizado"]
type StrPath = str | PathLike[str]

__all__ = ["MessageLog", "MessageType"]
