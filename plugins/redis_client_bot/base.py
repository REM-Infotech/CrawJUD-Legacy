"""Provide base functionality for Redis Client integration with abstract interface definition."""

from abc import ABC

from redis import Redis


class BaseRedisClient(Redis, ABC):
    """Provide base functionality for Redis Client integration with abstract interface definition.

    This abstract base class extends Redis functionality for Any Application(Flask, Quart, etc)
        applications by combining.

    Redis base features with an abstract interface, allowing for custom implementations.
    """
