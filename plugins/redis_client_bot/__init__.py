"""Redis client extension for WSGI | ASGI applications."""

from contextlib import suppress
from typing import Any, Awaitable, Optional, Union

from .base import BaseRedisClient
from .base import Redis as RedisBase
from .config import ConfigRedis
from .hybrid import HybridFunction  # noqa: F401


class Redis(BaseRedisClient):
    """Implement a WSGI | ASGI extension for Redis integration with comprehensive configuration support.

    This class provides a seamless integration between WSGI | ASGI applications and Redis,
    supporting both URL-based and parameter-based configuration methods.

    Attributes:
        redis_client: A Redis client instance configured with application settings.
        redis_params: Configuration settings for the Redis client.

    """

    redis_params: ConfigRedis
    _client: BaseRedisClient

    def __init__(self, app: Any = None) -> None:
        """Initialize the WSGI | ClientRedis extension with optional immediate configuration.

        Args:
            app (Any, optional): WSGI | ASGI application instance to configure. Defaults to None.
                If provided, automatically initializes the Redis connection.

        """
        self.redis_client = None
        if app:
            self.init_app(app)

    @property
    def redis_client(self) -> BaseRedisClient:
        """Get the Redis client instance.

        Returns:
            BaseRedisClient: The Redis client instance.

        """
        return self._client

    @redis_client.setter
    def redis_client(self, value: BaseRedisClient) -> None:
        """Set the Redis client instance.

        Args:
            value (BaseRedisClient): The Redis client instance to set.

        """
        self._client = value

    @classmethod
    def import_from_string(cls, path: str) -> object:
        """Import a class or module from a string path.

        Args:
            path (str): The path to the class or module to import.

        Returns:
            Any: The imported class or module.

        """
        from importlib import import_module

        return import_module(path)

    def config_from_object(self, obj: object | str | dict) -> None:
        """Configure Redis client using WSGI | ASGI configuration object.

        Args:
            obj (object | str | dict): Configuration object to load settings from.

        Returns:
            None

        """
        args = {}
        if isinstance(obj, str):
            obj = self.import_from_string(obj)
            for key in dir(obj):
                args.update({key: getattr(obj, key)})

        elif isinstance(obj, dict):
            args = obj

        self.redis_params = ConfigRedis.configure(args)

    def _config_to_app(self, app: Any) -> None:
        """Configure Redis client with WSGI | ASGI application settings."""
        with suppress(ImportError):
            self.config_from_object(app.config.get("REDIS_CONFIG", {}))
            from quart import Quart  # noqa: F401

            if isinstance(app, Quart):
                app.extensions["redis"] = self
                self.config_from_object(app.config.get("REDIS_CONFIG", {}))
                return

        with suppress(ImportError):
            from flask import Flask

            if isinstance(app, Flask):
                app.extensions["redis"] = self
                self.config_from_object(app.config.get("REDIS_CONFIG", {}))
                return

        with suppress(ImportError):
            from starlette.applications import Starlette  # type: ignore # noqa: PGH003

            if isinstance(app, Starlette):
                raise NotImplementedError("Starlette not supported app initialization")

        with suppress(ImportError):
            from fastapi import FastAPI  # type: ignore # noqa: PGH003

            if isinstance(app, FastAPI):
                app: FastAPI = app
                raise NotImplementedError("FastAPI not supported app initialization")

    def init_app(
        self,
        app: Any = None,
        config: Optional[Union[object, dict]] = None,
    ) -> None:
        """Configure Redis client with WSGI | ASGI application settings.

        Sets up Redis connection using either REDIS_URL or individual configuration parameters
        from WSGI | ASGI config. Supports comprehensive Redis client configuration including SSL,
        connection timeouts, and encoding options.

        Args:
            app (Any, optional): WSGI | ASGI application instance to configure. Defaults to None.
            config (Optional[object, dict], optional): Configuration object or dictionary to load settings from if app.

        Returns:
            None

        Note:
            Configuration can be provided either through REDIS_URL or individual parameters.
            When both are present, REDIS_URL takes precedence with individual params as overrides.

        """
        # Obter URL se fornecida

        if config:
            self.config_from_object(config)

        elif app:
            self._config_to_app(app)

        else:
            raise ValueError("No configuration provided for Redis client")

        redis_url = self.redis_params.url_server
        kwargs_ = self.redis_params.kwargs_config

        if redis_url:
            self.redis_client = RedisBase.from_url(
                redis_url,
                **{k: v for k, v in kwargs_.items() if v is not None},
            )
        else:
            self.redis_client = RedisBase(
                **{k: v for k, v in kwargs_.items() if v is not None},
            )

        # Adicionar a extensão ao app

    async def hgetall(
        self,
        name: tuple[str] | str,
        keys: Optional[list[str]] = None,
        **kwargs: str,
    ) -> Awaitable[dict] | dict:
        """Get all fields and values from a hash.

        Args:
            name (tuple[str] | str): The name of the hash.
            keys (Optional[list[str]]): A list of keys to get the values for.
            **kwargs (str): Variable number of arguments to construct the hash key.

        Returns:
            dict: A dictionary containing all fields and values from the hash.

        Example:
            >>> redis_client.hgetall(("process", "1234", "logs"))
            {"field1": "value1", "field2": "value2"}

            >>> redis_client.hgetall(name="process:1234:logs")
            {"field1": "value1", "field2": "value2"}

            >>> redis_client.hgetall("process:1234:logs", keys=["process", "logs"])
            {"field1": "value1", "field2": "value2"}


        """
        name = kwargs.get("name", name)
        keys = kwargs.get("keys", keys)
        if not keys:
            keys = [name]

        if ":" not in name and isinstance(name, tuple):
            name = ":".join(name)
        return self.redis_client.execute_command("HGETALL", name, keys=keys)

    async def hget(
        self,
        name: tuple[str] | str,
        key: str,
        keys: Optional[list[str]] = None,
        **kwargs: str,
    ) -> Awaitable[str] | str:
        """Get the value of a field from a hash.

        Args:
            name (): The name of the hash.
            key (str): The key of the
            keys (Optional[list[str]]): A list of keys to get the values for.
            **kwargs (str): Arbitrary keyword arguments.

        Returns:
            str: The value of the requested field.

        Example:
            >>> redis_client.hget("process", "1234", "logs", "field1")
            "value1"

            >>> redis_client.hget("process", "1234", "logs", key="field1")
            "value1"

            >>> redis_client.hget(name="process:1234:logs", key="field1")
            "value1"

        """
        name = kwargs.get("name", name)
        key = kwargs.get("key", key)
        keys = kwargs.get("keys", keys)
        if not keys:
            keys = [name]

        if ":" not in name and isinstance(name, tuple):
            name = ":".join(name)

        return self.redis_client.execute_command("HGET", name, key, keys=keys)
