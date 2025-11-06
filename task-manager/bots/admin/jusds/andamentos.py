"""empty."""

from typing import NoReturn

from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401

from bots.resources.elements import jusds as el  # noqa: F401
from common.exceptions import ExecutionError

from .master import JusdsBot


def raise_error(message: str) -> NoReturn:
    """Empty.

    Raises:
        ExecutionError: ExecutionError

    """
    raise ExecutionError(message=message)


class Andamentos(JusdsBot):
    """empty."""

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

        self.finalizar_execucao()

    def queue(self) -> None:
        pass
