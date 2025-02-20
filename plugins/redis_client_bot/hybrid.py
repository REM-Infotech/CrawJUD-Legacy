"""A class that allows for synchronous or asynchronous function calls."""

import asyncio
import functools
from typing import Any, Callable


class HybridFunction:
    """A class that allows for synchronous or asynchronous function calls."""

    def __init__(self, func: Callable[[], None]) -> None:
        """Initialize the HybridFunction class with a function."""
        functools.update_wrapper(self, func)
        self.func = func

    def __call__(self, *args: str | Any, **kwargs: str | Any) -> Any:
        """Call the function synchronously or asynchronously based on its type."""
        if asyncio.iscoroutinefunction(self.func):
            return asyncio.run(self.func(*args, **kwargs))
        return self.func(*args, **kwargs)

    # async def async_call(self, *args: str | Any, **kwargs: str | Any) -> Any:
    #     """Call the function asynchronously."""
    #     return await self.func(*args, **kwargs)

    def __doc__(self) -> str:
        """Return the function's docstring."""
        return self.func.__doc__
