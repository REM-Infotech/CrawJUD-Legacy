"""Define the configuration settings for the Redis client."""

from __future__ import annotations

from typing import Optional, Union

from redis import CredentialProvider
from redis.cache import CacheConfig, CacheInterface

from plugins import convert_to_type

ValueTypes = Union[str, int, float, bool, CredentialProvider, CacheConfig, CacheInterface, dict, list]

TypesArg = dict[str, ValueTypes]


class ConfigRedis:
    """Define the configuration settings for the Redis client."""

    host = "localhost"
    port = 6379
    db = 0
    password = None
    socket_timeout = None
    socket_connect_timeout = None
    socket_keepalive = None
    socket_keepalive_options = None
    connection_pool = None
    unix_socket_path = None
    encoding = "utf-8"
    encoding_errors = "strict"
    charset = None
    errors = None
    decode_responses = True
    retry_on_timeout = False
    retry_on_error = None
    ssl = False
    ssl_keyfile = None
    ssl_certfile = None
    ssl_cert_reqs = "required"
    ssl_ca_certs = None
    ssl_ca_path = None
    ssl_ca_data = None
    ssl_check_hostname = False
    ssl_password = None
    ssl_validate_ocsp = False
    ssl_validate_ocsp_stapled = False
    ssl_ocsp_context = None
    ssl_ocsp_expected_cert = None
    ssl_min_version = None
    ssl_ciphers = None
    max_connections = None
    single_connection_client = False
    health_check_interval = 0
    client_name = None
    lib_name = "redis-py"
    username = None
    retry = None
    redis_connect_func = None
    credential_provider: Optional[CredentialProvider] = None
    protocol: Optional[int] = 2
    cache: Optional[CacheInterface] = None
    cache_config: Optional[CacheConfig] = None
    url_server = "redis://localhost:6379/0"

    kwargs_config = {}

    @classmethod
    def configure(cls, args: TypesArg) -> ConfigRedis:
        """Configure the Redis client with the provided settings."""
        object_ = ConfigRedis
        dicted_args = {}

        for key in dir(ConfigRedis):
            value = args.get(key)
            if value:
                setattr(object_, key, convert_to_type(value))

            if "__" not in key:
                val = getattr(object_, key)
                if val is not None:
                    dicted_args.update({key: val})

        object_.kwargs_config = dicted_args

        return object_

    def __repr__(self) -> str:
        """Return a string representation of the ConfigRedis object."""
        return f"{ConfigRedis.__class__.__name__}({ConfigRedis.__dict__})"
