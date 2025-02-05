"""Module for initializing and configuring application logger."""

import logging
import os
from logging import DEBUG, Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)


def init_log(
    L_F: str = None,  # noqa: N803
    L_LVL: int = None,  # noqa: N803
    mx_bt: int = None,
    bkp_ct: int = None,
    *args: tuple,
    **kwargs: dict,
) -> Logger:
    """Initialize and configure logging for the application.

    Args:
        L_F (str, optional): The name of the log file. Defaults to "app.log".
        L_LVL (int, optional): The logging level. Defaults to logger.DEBUG.
        mx_bt (int, optional): The maximum size of the log file in bytes before it is rotated. Defaults to 1MB.
        bkp_ct (int, optional): The number of backup log files to keep. Defaults to 1.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Logger: Configured logger instance.

    """
    L_F: str = L_F or str(kwargs.pop("L_F", "app.log"))  # noqa: N806
    L_LVL: int = L_LVL or int(kwargs.pop("L_LVL", DEBUG))  # noqa: N806
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024 * 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 1))

    logger.setLevel(L_LVL)

    # Formatter
    # formatter = logger.Formatter(
    #    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # )

    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(Path(__file__).parent.resolve(), L_F),
        maxBytes=mx_bt,
        backupCount=bkp_ct,
    )
    # file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logger.StreamHandler()
    # console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
