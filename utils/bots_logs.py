"""Module for initializing and configuring application logger."""

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from os import getenv
from pathlib import Path
from typing import Any
from uuid import uuid4

import socketio
from aiopath import AsyncPath
from tqdm import tqdm

logger = logging.getLogger(__name__)


class SocketIOLogClientHandler(logging.Handler):
    """Logging handler that sends log messages to a Socket.IO server."""

    _app = getenv("APPLICATION_APP")
    formatter: logging.Formatter = None
    level: int = logging.INFO
    server_url: str = "http://localhost:7000"

    def __init__(self, server_url: str = "http://localhost:7000", *args: str | int, **kwargs: str | int) -> None:
        """Initialize the handler with the server URL."""
        super().__init__()
        self.sio = socketio.Client()
        self.server_url = server_url
        self._connect()
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def _connect(self) -> None:
        try:
            self.sio.connect(
                url=self.server_url,
                namespaces=[
                    "/application_logs",
                    f"/{self._app}",
                ],
                wait_timeout=5,
            )
        except Exception as e:
            tqdm.write(f"SocketIO connection error: {e}")

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log message to the server via Socket.IO."""
        try:
            msg = self.format(record)
            self.sio.emit(f"{self._app}_logs", msg, namespace=f"/{self._app}")
        except Exception:
            self.handleError(record)


async def asyncinit_log_dict(
    log_file: str | Path = None,
    log_level: int = None,
    mx_bt: int = None,
    bkp_ct: int = None,
    **kwargs: str | int,
) -> dict[str, Any]:
    """Initialize and configure logging for the application with Socket.IO handler."""
    log_file: str = log_file or str(kwargs.pop("log_file", "app/logs"))  # noqa: N806
    log_level: int = log_level or int(kwargs.pop("log_level", logging.DEBUG))  # noqa: N806
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 5))

    max_bytes = mx_bt * 1024

    logger.setLevel(logging.INFO)

    # Formatter
    log_path_file = str(log_file)

    if log_file == "app/logs":
        log_path: Path = await AsyncPath(Path(__file__)).cwd()
        log_path: Path = await log_path.joinpath(log_file).resolve()
        log_path_file = str(log_path.joinpath("app.log"))

        if not await log_path.exists():
            await log_path.mkdir(parents=True, exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)s:%(name)s:%(message)s",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "socketio_handler": {
                "class": "utils.bots_logs.SocketIOLogClientHandler",
                "server_url": "http://localhost:7000",
                "level": "DEBUG",
                "formatter": "default",
            },
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "default",
                "filename": log_path_file,
                "maxBytes": max_bytes,
                "backupCount": bkp_ct,
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["default", "socketio_handler", "file_handler"],
        },
        "loggers": {
            f"app.{getenv('APPLICATION_APP')}": {
                "level": "DEBUG",
                "handlers": ["default", "socketio_handler", "file_handler"],
                "propagate": False,
            },
        },
    }


async def asyncinit_log(
    log_file: str | Path = None,
    log_level: int = None,
    mx_bt: int = None,
    bkp_ct: int = None,
    **kwargs: dict,
) -> Logger:
    """Initialize and configure logging for the application with Socket.IO handler.

    Além dos handlers de arquivo e console, adiciona o handler SocketIOLogClientHandler
    para transmitir logs para o servidor de logs via Socket.IO (por exemplo, para o Quart).
    """
    logger = logging.getLogger(uuid4().hex)
    log_file: str = log_file or str(kwargs.pop("log_file", "app/logs"))  # noqa: N806
    log_level: int = log_level or int(kwargs.pop("log_level", logging.DEBUG))  # noqa: N806
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 5))

    max_bytes = mx_bt * 1024

    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_path_file = str(log_file)

    if log_file == "app/logs":
        log_path: Path = await AsyncPath(Path(__file__)).cwd()
        log_path: Path = await log_path.joinpath(log_file).resolve()
        log_path_file = str(log_path.joinpath("app.log"))

        if not await log_path.exists():
            await log_path.mkdir(parents=True, exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        log_path_file,
        maxBytes=max_bytes,
        backupCount=bkp_ct,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Socket.IO handler (cliente)
    socketio_handler = SocketIOLogClientHandler(server_url="http://localhost:7000")
    socketio_handler.setLevel(log_level)
    socketio_handler.setFormatter(formatter)
    logger.addHandler(socketio_handler)
    logger.info("Logger initialized.")

    return logger


def init_log(
    log_file: str = None,
    log_level: int = None,
    mx_bt: int = None,
    bkp_ct: int = None,
    *args: tuple,
    **kwargs: dict,
) -> Logger:
    """Sincronamente inicializa e configura o logger, incluindo o handler Socket.IO."""
    logger = logging.getLogger(uuid4().hex)
    log_file: str = log_file or str(kwargs.pop("log_file", "app/logs"))
    log_level: int = log_level or int(kwargs.pop("log_level", logging.DEBUG))
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024 * 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 1))

    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if log_file == "app/logs":
        log_path_file = Path(__file__).cwd().joinpath(log_file).joinpath("app.log").resolve()
        if not log_path_file.parent.exists():
            log_path_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        log_path_file = Path(log_file).resolve()

    # File handler
    file_handler = RotatingFileHandler(
        str(log_path_file),
        maxBytes=mx_bt,
        backupCount=bkp_ct,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Socket.IO handler (cliente)
    socketio_handler = SocketIOLogClientHandler(server_url="http://localhost:7000")
    socketio_handler.setFormatter(formatter)
    logger.addHandler(socketio_handler)

    return logger
