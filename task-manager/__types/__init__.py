from datetime import datetime, timedelta
from os import PathLike
from typing import Any, Literal, ParamSpec, TypeVar

type AnyType = Any

P = ParamSpec("P", bound=Any)
T = TypeVar("T", bound=AnyType)

type MessageType = Literal["info", "log", "error", "warning", "success"]
type ListPartes = list[tuple[list[dict[str, str]], list[dict[str, str]]]]
type MethodsSearch = Literal["peticionamento", "consulta"]
type PolosProcessuais = Literal["Passivo", "Ativo"]
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes
type Dict = dict[str, PyStrings | PyNumbers]
type ListDict = list[Dict]
type StatusBot = Literal["Inicializando", "Em Execução", "Finalizado"]
type StrPath = str | PathLike[str]
