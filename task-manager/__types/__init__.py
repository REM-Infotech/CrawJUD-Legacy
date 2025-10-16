from datetime import datetime, timedelta
from typing import Any, Literal

type AnyType = Any

type ListPartes = list[tuple[list[dict[str, str]], list[dict[str, str]]]]
type MethodsSearch = Literal["peticionamento", "consulta"]
type PolosProcessuais = Literal["Passivo", "Ativo"]
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes
type Dict = dict[str, PyStrings | PyNumbers]
type ListDict = list[Dict]
