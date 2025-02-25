"""Web types module."""

from typing import Dict, List, Tuple, TypeVar, Union

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
AnyType = TypeVar("AnyType", bound=binds)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")
AnyStr = TypeVar("AnyStr", bound=strings)

T = TypeVar("T", bound=QuartForm)  # Tipo genérico baseado em Pai
