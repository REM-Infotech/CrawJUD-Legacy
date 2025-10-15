"""Defina tipos e aliases utilizados em toda a aplicação CrawJUD.

Este módulo centraliza definições de tipos, facilitando a tipagem
de dados, parâmetros e retornos em funções e classes do projeto.

"""

from __future__ import annotations

from datetime import datetime, timedelta
from os import PathLike
from typing import Literal, ParamSpec, TypedDict, TypeVar

from crawjud.interfaces.dict.bot import BotData

# Tipos de retorno das funções

T = TypeVar("T")
P = ParamSpec("P")


class ColorsDict(TypedDict):
    info: Literal["cyan"]
    log: Literal["yellow"]
    error: Literal["red"]
    warning: Literal["magenta"]
    success: Literal["green"]


type ConfigName = Literal["default"]
type DictData = dict[str, str | datetime]
type ListData = list[DictData]
# Tipos primitivos do Python
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes

# Tipos de tuplas, listas e dicionários
type TupleType = tuple[PyStrings | PyNumbers]
type ListType = list[PyStrings | PyNumbers]
type DictType = dict[str, PyStrings | PyNumbers]

# Tipo de armazenamento de dados
type DataStores = TupleType | ListType | set | DictType
type Binds = PyNumbers | PyStrings | TupleType | ListType | DictType

# Definição do tipo "StrPath"
type StrPath = str | PathLike
type ReturnFormataTempo = datetime | float | int | bool | str

type Methods = list[
    Literal["GET", "POST", "PUT", "DELETE", "UPDATE", "INSERT", "OPTIONS"]
]
type ListPartes = list[tuple[list[dict[str, str]], list[dict[str, str]]]]
type ProcessInfo = dict[str, str | int | datetime]

__all__ = ["BotData"]
