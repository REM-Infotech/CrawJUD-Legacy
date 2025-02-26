"""Module config project log."""

import logging
from os import getenv
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def log_cfg(
    log_file: str | Path = None,
    log_level: int = None,
    mx_bt: int = None,
    bkp_ct: int = None,
    **kwargs: str | int,
) -> tuple[dict[str, Any], str]:
    """Initialize and configure logging for the application with Socket.IO handler."""
    log_file: str = log_file or str(kwargs.pop("log_file", "app/logs"))
    log_level: int = log_level or int(kwargs.pop("log_level", logging.DEBUG))
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 5))

    max_bytes = mx_bt * 1024

    logger.setLevel(logging.INFO)

    logger_name = kwargs.get("logger_name", __name__)
    log_path_file = str(log_file)

    if log_file == "app/logs":
        log_path: Path = Path(Path(__file__)).cwd()
        log_path: Path = log_path.joinpath(log_file).resolve()
        log_path_file = str(log_path.joinpath("app.log"))

        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)s:%(name)s:%(message)s",
            },
        },
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
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
            "handlers": ["stream", "file_handler"],
        },
        "loggers": {
            logger_name: {
                "level": "DEBUG",
                "handlers": ["stream", "file_handler"],
                "propagate": False,
            },
        },
    }

    if getenv("SERVER_MANAGEMENT"):
        config["handlers"]["stream"]["class"] = "logging.NullHandler"
        config["handlers"]["redis_handler"] = {
            "class": "crawjud.logs.handlers.RedisHandler",
            "uri": getenv("REDIS_URL", "redis://localhost:6379/0"),
            "level": "DEBUG",
            "formatter": "",
        }
        config["formatters"]["json"] = {
            "()": "crawjud.logs.handlers.JsonFormatter",
        }
        config["handlers"]["redis_handler"]["formatter"] = "json"
        config["root"]["handlers"].append("redis_handler")
        config["loggers"][logger_name]["handlers"].append("redis_handler")

    return config, logger_name
