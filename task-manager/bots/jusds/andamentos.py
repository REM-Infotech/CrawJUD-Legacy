"""empty."""

from typing import NoReturn

from app.common.exceptions.bot import ExecutionError
from app.decorators import shared_task
from app.decorators.bot import wrap_cls
from controllers.jusds import JusdsBot
from resources.elements import jusds as el  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401


def raise_error(message: str) -> NoReturn:
    """Empty.

    Raises:
        ExecutionError: ExecutionError

    """
    raise ExecutionError(message=message)


@shared_task(name="jusds.andamentos", bind=True, context=ContextTask)
@wrap_cls
class Andamentos(JusdsBot):
    """empty."""

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

        self.finalize_execution()

    def queue(self) -> None:
        pass
