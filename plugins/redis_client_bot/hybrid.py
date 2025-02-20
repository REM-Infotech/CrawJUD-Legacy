"""A class that allows for synchronous or asynchronous function calls."""

import asyncio
from typing import Any, Callable


class HybridFunction:
    """A class that allows for synchronous or asynchronous function calls."""

    def __init__(self, func: Callable[[]]) -> None:
        """Initialize the HybridFunction class with a function."""
        self.func = func

    def __call__(self, *args: str | any, **kwargs: str | any) -> Any:
        """Call the function synchronously or asynchronously based on its type."""
        if asyncio.iscoroutinefunction(self.func):
            return asyncio.run(self.func(*args, **kwargs))
        return self.func(*args, **kwargs)

    async def async_call(self, *args: str | any, **kwargs: str | any) -> Any:
        """Call the function asynchronously."""
        return await self.func(*args, **kwargs)
