import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from logging import DEBUG, Logger


def init_log(L_F=None, L_LVL=None, mx_bt=None, bkp_ct=None, *args, **kwargs) -> Logger:
    """
    Initialize and configure logging for the application.

    Args:
        L_F (str): The name of the log file. Defaults to "app.log".
        L_LVL (int): The logging level. Defaults to logging.DEBUG.
        mx_bt (int): The maximum size of the log file in bytes before it is rotated. Defaults to 1MB.
        bkp_ct (int): The number of backup log files to keep. Defaults to 1.
    Returns:
        Logger: Configured logger instance.
    """
    L_F: str = L_F or str(kwargs.pop("L_F", "app.log"))
    L_LVL: int = L_LVL or int(kwargs.pop("L_LVL", DEBUG))
    mx_bt: int = mx_bt or int(kwargs.pop("mx_bt", 1024 * 1024))
    bkp_ct: int = bkp_ct or int(kwargs.pop("bkp_ct", 1))

    logger = logging.getLogger(__name__)
    logger.setLevel(L_LVL)

    # Formatter
    # formatter = logging.Formatter(
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
    console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
