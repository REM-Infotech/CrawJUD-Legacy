"""ASGI Server Thread Management Module.

This module provides custom Thread implementations for managing ASGI server execution
with proper exception handling and graceful shutdown capabilities. It extends the
standard threading.Thread class to add safety features for running web socket servers.

Key Components:
    - CustomThread: Enhanced Thread class with exception propagation
    - ASGIServer: Customized ASGI server implementation based on uvicorn

Example:
    from thead_asgi import ASGIServer, CustomThread

    # Create and start a SocketIO server
    app = SocketIO()
    server_thread = ASGIServer.startio_srv(app)

    # The server can be shutdown gracefully
    server_thread.terminate()
    server_thread.join()

"""

from __future__ import annotations

import asyncio
import os
import ssl
from configparser import RawConfigParser
from threading import Thread
from typing import IO, Any, Callable, Self

import uvicorn
from socketio import ASGIApp
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


class CustomThread(Thread):
    """Enhanced Thread class for ASGI server management.

    This class extends Thread to provide robust exception handling and controlled
    shutdown capabilities when running ASGI servers. It captures and propagates
    exceptions that occur during server execution to the main thread.

    Attributes:
        exc_bot (Exception): Captured exception during execution, None if no error
        _target (ASGIServer): The ASGI server instance being managed

    Example:
        server = ASGIServer(config)
        thread = CustomThread(target=server)
        thread.start()

        # Shutdown gracefully
        thread.terminate()
        thread.join()  # Will raise any captured exception

    """

    exc_bot: Exception = None
    _target: ASGIServer

    def join(self) -> None:
        """Block until the bot process completes and propagate any captured exceptions.

        Now triggers shutdown via terminate().
        """
        self.terminate()
        Thread.join(self)
        if self.exc_bot:
            raise self.exc_bot

    def run(self) -> None:
        """Execute the bot's target function and capture any exceptions that occur.

        Wraps the execution of the target function in a try-except block to capture
        any exceptions that occur during bot operation. Stores captured exceptions
        in the exc_bot attribute.
        """
        self.exc_bot = None

        try:
            self.application = self._target
            target = self._target.run_app
            target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e

    def terminate(self) -> None:
        """Trigger graceful shutdown of the ASGI server from within the thread."""
        if hasattr(self, "_target"):
            self._target.should_exit = True

    def chk_except(self) -> None:
        """Check and raise any exceptions that occurred during bot execution.

        This method allows checking for exceptions without joining the process.
        It should be used when you want to verify the bot's execution state
        without waiting for completion.

        Raises:
            Exception: Any exception that was captured during bot execution.

        """
        if self.exc_bot:
            raise self.exc_bot


class ASGIServer(uvicorn.Server):
    """Extended ASGI server implementation with additional control features.

    This class builds upon uvicorn.Server to provide simplified server setup
    and management capabilities, particularly focused on SocketIO applications.
    It includes methods for easy server startup and configuration.

    Attributes:
        joinned_thread (bool): Tracks if the server thread has been joined

    Example:
        app = SocketIO()
        server_thread = ASGIServer.startio_srv(app)
        # Server runs on 127.0.0.1:7000 by default

    """

    joinned_thread = False

    @classmethod
    def startio_srv(cls, app: ASGIApp) -> CustomThread:
        """Start SocketIO server."""
        hostname = "127.0.0.1"
        port = 7000
        log_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "handlers": {
                "null": {
                    "class": "logging.NullHandler",
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["null"],
            },
        }
        application = cls.setup_app(
            app=app,
            host=hostname,
            port=port,
            log_config=log_config,
        )
        io_srv = CustomThread(target=application)
        io_srv.start()

        return io_srv

    def run_app(self, *args: Any, **kwargs: Any) -> None:
        """Run the ASGI server."""
        self.run()

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
