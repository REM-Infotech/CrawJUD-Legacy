"""ASGI server module."""

import asyncio
import os
import ssl
import sys
from configparser import RawConfigParser
from threading import Thread  # noqa: F401
from typing import IO, Any, Callable, Self

import inquirer
import uvicorn
from socketio import ASGIApp, AsyncServer
from tqdm import tqdm  # noqa: F401
from uvicorn._types import ASGIApplication
from uvicorn.config import (
    HTTP_PROTOCOLS,  # noqa: F401
    INTERFACES,  # noqa: F401
    LIFESPAN,  # noqa: F401
    LOG_LEVELS,  # noqa: F401
    LOGGING_CONFIG,
    LOOP_SETUPS,  # noqa: F401
    SSL_PROTOCOL_VERSION,
    WS_PROTOCOLS,  # noqa: F401
    Config,  # noqa: F401
    HTTPProtocolType,
    InterfaceType,
    LifespanType,
    LoopSetupType,
    WSProtocolType,
)

io = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=10,
)


class ASGIServer(uvicorn.Server):
    """ASGI server class."""

    @classmethod
    def setup_app(
        cls,
        app: ASGIApplication | Callable[..., Any] | str,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
        uds: str | None = None,
        fd: int | None = None,
        loop: LoopSetupType = "auto",
        http: type[asyncio.Protocol] | HTTPProtocolType = "auto",
        ws: type[asyncio.Protocol] | WSProtocolType = "auto",
        ws_max_size: int = 16777216,
        ws_max_queue: int = 32,
        ws_ping_interval: float | None = 20.0,
        ws_ping_timeout: float | None = 20.0,
        ws_per_message_deflate: bool = True,
        lifespan: LifespanType = "auto",
        interface: InterfaceType = "auto",
        reload: bool = False,
        reload_dirs: list[str] | str | None = None,
        reload_includes: list[str] | str | None = None,
        reload_excludes: list[str] | str | None = None,
        reload_delay: float = 0.25,
        workers: int | None = None,
        env_file: str | os.PathLike[str] | None = None,
        log_config: dict[str, Any] | str | RawConfigParser | IO[Any] | None = LOGGING_CONFIG,
        log_level: str | int | None = None,
        access_log: bool = True,
        proxy_headers: bool = True,
        server_header: bool = True,
        date_header: bool = True,
        forwarded_allow_ips: list[str] | str | None = None,
        root_path: str = "",
        limit_concurrency: int | None = None,
        backlog: int = 2048,
        limit_max_requests: int | None = None,
        timeout_keep_alive: int = 5,
        timeout_graceful_shutdown: int | None = None,
        ssl_keyfile: str | os.PathLike[str] | None = None,
        ssl_certfile: str | os.PathLike[str] | None = None,
        ssl_keyfile_password: str | None = None,
        ssl_version: int = SSL_PROTOCOL_VERSION,
        ssl_cert_reqs: int = ssl.CERT_NONE,
        ssl_ca_certs: str | None = None,
        ssl_ciphers: str = "TLSv1",
        headers: list[tuple[str, str]] | None = None,
        use_colors: bool | None = None,
        app_dir: str | None = None,
        factory: bool = False,
        h11_max_incomplete_event_size: int | None = None,
    ) -> Self:
        """Create an ASGI server instance with the given configuration."""
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            uds=uds,
            fd=fd,
            loop=loop,
            http=http,
            ws=ws,
            ws_max_size=ws_max_size,
            ws_max_queue=ws_max_queue,
            ws_ping_interval=ws_ping_interval,
            ws_ping_timeout=ws_ping_timeout,
            ws_per_message_deflate=ws_per_message_deflate,
            lifespan=lifespan,
            interface=interface,
            reload=reload,
            reload_dirs=reload_dirs,
            reload_includes=reload_includes,
            reload_excludes=reload_excludes,
            reload_delay=reload_delay,
            workers=workers,
            env_file=env_file,
            log_config=log_config,
            log_level=log_level,
            access_log=access_log,
            proxy_headers=proxy_headers,
            server_header=server_header,
            date_header=date_header,
            forwarded_allow_ips=forwarded_allow_ips,
            root_path=root_path,
            limit_concurrency=limit_concurrency,
            backlog=backlog,
            limit_max_requests=limit_max_requests,
            timeout_keep_alive=timeout_keep_alive,
            timeout_graceful_shutdown=timeout_graceful_shutdown,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            ssl_keyfile_password=ssl_keyfile_password,
            ssl_version=ssl_version,
            ssl_cert_reqs=ssl_cert_reqs,
            ssl_ca_certs=ssl_ca_certs,
            ssl_ciphers=ssl_ciphers,
            headers=headers,
            use_colors=use_colors,
            factory=factory,
            h11_max_incomplete_event_size=h11_max_incomplete_event_size,
        )
        return cls(config)

    def __init__(
        self,
        config: uvicorn.Config,
    ) -> None:
        """Initialize the ASGI server."""
        super().__init__(config)


class MasterApp:
    """Master application class."""

    thead_io = None

    def __init__(self) -> None:
        """Initialize the ASGI server."""
        self.asgi_app = ASGIApp(io)
        app = self.asgi_app
        hostname = "127.0.0.1"
        port = 7000
        self.application = ASGIServer.setup_app(app=app, host=hostname, port=port)
        self.application.run()

    def prompt(self) -> None:
        """Prompt the user for server options."""
        server_options = inquirer.List(
            "application_list",
            message="Select application",
            choices=["ASGI Server", "Celery Worker", "Celery Beat", "Close Server"],
        )

        server_answer = inquirer.prompt([server_options])

        if server_answer.get("application_list") == "Close Server":
            asyncio.run(self.application.shutdown())
            sys.exit(0)

        if server_answer.get("application_list") == "ASGI Server":
            pass
