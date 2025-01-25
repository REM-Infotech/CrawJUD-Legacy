from __future__ import annotations

from .shared import PropertiesCrawJUD
from typing import Callable, Tuple
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class Emulate(PropertiesCrawJUD):

    def otherutils(self) -> OtherUtils:
        from .Utils import OtherUtils

        return OtherUtils()

    @property
    def elements(self) -> ESAJ_AM | ELAW_AME | PJE_AM | PROJUDI_AM:
        from .Utils import ElementsBot

        return ElementsBot().Elements

    @property
    def interact(self) -> Interact:
        from .Utils import Interact

        return Interact()

    @property
    def isStoped(self) -> bool:

        file_check = Path(self.output_dir_path).resolve().joinpath(f"{self.pid}.flag")
        return file_check.exists()

    @property
    def dataFrame(self) -> Callable[[], list[dict[str, str]]]:

        return Emulate.otherutils(self).dataFrame

    @property
    def Auth_Bot(self) -> Callable[[], bool]:
        from .Utils import AuthBot

        return AuthBot().auth

    @property
    def printtext(self) -> PrintBot:

        from .Utils import PrintBot

        return PrintBot()

    @property
    def DriverLaunch(self) -> Callable[..., Tuple[WebDriver, WebDriverWait]]:
        from .Utils import DriverBot

        return DriverBot().DriverLaunch

    @property
    def MakeXlsx(self) -> Make_xls:

        from .Utils import MakeXlsx as Make_xls

        return Make_xls()

    def search_bot(self):

        from .Utils import SearchBot

        return SearchBot().search_()

    @property
    def append_error(self) -> Callable[..., None]:

        return Emulate.otherutils(self).append_error

    @property
    def append_success(self) -> Callable[..., None]:

        return Emulate.otherutils(self).append_success


if __name__ == "__main__":
    from .Utils import (
        PrintBot,
        Interact,
        ELAW_AME,
        ESAJ_AM,
        PJE_AM,
        PROJUDI_AM,
        OtherUtils,
        MakeXlsx as Make_xls,
    )
