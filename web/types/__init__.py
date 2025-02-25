"""Web types module."""

from typing import Any, TypeVar

from quart import Request
from quart_wtf import QuartForm

AnyType = TypeVar("AnyType", str, bytes, Any, Request)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")
AnyStr = TypeVar("AnyStr", str, bytes)

T = TypeVar("T", bound=QuartForm)  # Tipo genérico baseado em Pai
