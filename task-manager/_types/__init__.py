from datetime import datetime, timedelta
from typing import Any, Literal

type AnyType = Any
type DictData = dict[str, str | datetime]
type ListData = list[DictData]
type PolosProcessuais = Literal["Passivo", "Ativo"]
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes
type Dict = dict[str, PyStrings | PyNumbers]
