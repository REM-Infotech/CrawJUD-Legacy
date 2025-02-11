"""Module for initializing and configuring application logger."""

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiopath import AsyncPath

logger = logging.getLogger(__name__)


async def asyncinit_log(
    log_file: str = None,
    log_level: int = None,
    mx_bt: int = None,
    bkp_ct: int = None,
    *args: tuple,
    **kwargs: dict,
) -> Logger:
    """Initialize and configure logging for the application.

    Args:
        log_file (str, optional): The name of the log file. Defaults to "app.log".
        log_level (int, optional): The logging level. Defaults to logger.DEBUG.
        mx_bt (int, optional): The maximum size of the log file in bytes before it is rotated. Defaults to 1MB.
        bkp_ct (int, optional): The number of backup log files to keep. Defaults to 1.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Logger: Configured logger instance.

    """
    log_file: str = log_file or str(kwargs.pop("log_file", "app/logs"))  # noqa: N806
    log_level: int = log_level or int(kwargs.pop("log_level", logging.DEBUG))  # noqa: N806
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024 * 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 1))

    logger.setLevel(logging.INFO)
    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_path: Path = await AsyncPath(Path(__file__)).cwd()
    log_path: Path = await log_path.joinpath(log_file).resolve()
    log_path_file: Path = log_path.joinpath("app.log")

    # File handler
    if await log_path.exists() is False:
        await log_path.mkdir(parents=True, exist_ok=True)
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

    return logger


def init_log(
    log_file: str = None,
    log_level: int = None,
    mx_bt: int = None,
    bkp_ct: int = None,
    *args: tuple,
    **kwargs: dict,
) -> Logger:
    """Initialize and configure logging for the application.

    Args:
        log_file (str, optional): The name of the log file. Defaults to "app.log".
        log_level (int, optional): The logging level. Defaults to logger.DEBUG.
        mx_bt (int, optional): The maximum size of the log file in bytes before it is rotated. Defaults to 1MB.
        bkp_ct (int, optional): The number of backup log files to keep. Defaults to 1.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Logger: Configured logger instance.

    """
    log_file: str = log_file or str(kwargs.pop("log_file", "app/logs"))
    log_level: int = log_level or int(kwargs.pop("log_level", logging.DEBUG))
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024 * 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 1))

    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_path_file = Path(__file__).cwd().joinpath(log_file).joinpath("app.log").resolve()

    if log_path_file.parent.exists() is False:
        log_path_file.parent.mkdir(parents=True, exist_ok=True)

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

    return logger
