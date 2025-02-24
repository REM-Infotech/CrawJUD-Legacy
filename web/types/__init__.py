"""Web types module."""

from typing import Any, TypeVar

from quart import Request

AnyType = TypeVar("AnyType", str, bytes, Any, Request)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")
AnyStr = TypeVar("AnyStr", str, bytes)
