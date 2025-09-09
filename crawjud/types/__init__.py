"""Web types module."""

from datetime import datetime, timedelta
from typing import Dict, List, Literal, Tuple, TypeVar, Union

from quart_wtf import QuartForm

numbers = Union[int, float]
strings = Union[str, bytes]
TupleType = Tuple[Union[strings, numbers]]
ListType = List[Union[strings, numbers]]
DictType = Dict[str, Union[strings, numbers]]
datastores = Union[
    TupleType,
    ListType,
    set,
    DictType,
]

binds = Union[
    numbers,
    strings,
    TupleType,
    ListType,
    DictType,
]

Numbers = Union[int, float, complex, datetime, timedelta]
type TypeValues = Union[str, Numbers, list, tuple]
type SubDict = dict[str, Union[TypeValues, Numbers]]
type TypeHint = Union[list[str | Numbers | SubDict] | SubDict]

DataStores = TypeVar("DataStores", bound=datastores)
AnyType = TypeVar("AnyType", bound=binds)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")
AnyStr = TypeVar("AnyStr", bound=strings)
app_name = Literal["Quart", "Worker"]
T = TypeVar("T", bound=QuartForm)  # Tipo genérico baseado em Pai
