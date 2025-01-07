from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Callable, Dict, Union

from dotenv import load_dotenv
from openai import OpenAI
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = Dict[str, Union[TypeValues, Numbers]]


class classproperty:

    load_dotenv()
    OpenAI_client_ = OpenAI()

    appends_ = []
    another_append_ = []

    path_accepted_: str = ""
    vara_: str = ""
    _system: str = ""
    _state_or_client_: str = ""
    _type_log: str = "info"
    _message: str = ""
    _pid: str = ""
    kwrgs_: Dict[str, Union[TypeValues, SubDict]] = {}
    row_: int = 0
    message_error_: str = ""
    bot_data_: Dict[str, Union[TypeValues, SubDict]] = {}
    graphicMode_: str = "doughnut"
    out_dir: str = ""
    user_data_dir: str = ""
    cr_list_args: list[str] = []
    drv: WebDriver = None
    wt: WebDriverWait = None
    elmnt = None
    interact_ = None

    @property
    def appends(self) -> list:
        return self.appends_

    @appends.setter
    def appends(self, new_appends: list) -> None:
        self.appends_ = new_appends

    @property
    def another_append(self) -> list:
        return self.another_append_

    @another_append.setter
    def another_append(self, new_another_append: list) -> None:
        self.another_append_ = new_another_append

    @property
    def OpenAI_client(self) -> OpenAI:

        return self.OpenAI_client_

    @property
    def system(self) -> str:
        return classproperty._system

    @system.setter
    def system(self, system_: str) -> None:
        classproperty._system = system_

    @property
    def state_or_client(self) -> str:
        return classproperty._state_or_client_

    @state_or_client.setter
    def state_or_client(self, new_s: str) -> None:
        classproperty._state_or_client_ = new_s

    @property
    def type_log(self) -> str:
        return classproperty._type_log

    @type_log.setter
    def type_log(self, new_log: str) -> None:
        classproperty._type_log = new_log

    @property
    def pid(self) -> int:
        return classproperty._pid

    @pid.setter
    def pid(self, pid_) -> int:
        classproperty._pid = pid_

    @property
    def message(self) -> str:
        return classproperty._message

    @message.setter
    def message(self, new_msg: str) -> str:
        classproperty._message = new_msg

    @property
    def isStoped(self) -> bool:
        chk = os.path.exists(os.path.join(self.output_dir_path, f"{self.pid}.flag"))
        return chk

    @property
    def driver(self) -> WebDriver:  # pragma: no cover
        return classproperty.drv

    @driver.setter
    def driver(self, new_drv: WebDriver) -> None:  # pragma: no cover
        classproperty.drv = new_drv

    @property
    def wait(self) -> WebDriverWait:  # pragma: no cover
        return classproperty.wt

    @wait.setter
    def wait(self, new_wt: WebDriverWait) -> None:  # pragma: no cover
        classproperty.wt = new_wt

    @property
    def chr_dir(self) -> str:
        return classproperty.user_data_dir

    @chr_dir.setter
    def chr_dir(self, new_dir: str) -> None:
        classproperty.user_data_dir = new_dir

    @property
    def output_dir_path(self) -> str:
        return classproperty.out_dir

    @output_dir_path.setter
    def output_dir_path(self, new_outdir: str) -> None:
        classproperty.out_dir = new_outdir

    @property
    def kwrgs(self) -> dict:
        return classproperty.kwrgs_

    @kwrgs.setter
    def kwrgs(self, new_kwg) -> None:
        classproperty.kwrgs_ = new_kwg

    @property
    def row(self) -> int:
        return classproperty.row_

    @row.setter
    def row(self, new_row: int) -> None:
        classproperty.row_ = new_row

    @property
    def message_error(self) -> str:
        return classproperty.message_error_

    @message_error.setter
    def message_error(self, nw_m: str) -> str:
        classproperty.message_error_ = nw_m

    @property
    def graphicMode(self) -> str:
        return classproperty.graphicMode_

    @graphicMode.setter
    def graphicMode(self, new_graph) -> None:
        classproperty.graphicMode_ = new_graph

    @property
    def list_args(self) -> list[str]:  # pragma: no cover
        return [
            "--ignore-ssl-errors=yes",
            "--ignore-certificate-errors",
            "--display=:99",
            "--window-size=1600,900",
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--kiosk-printing",
        ]

    @list_args.setter
    def list_args(self, new_Args: list[str]) -> None:  # pragma: no cover
        classproperty.cr_list_args = new_Args

    @property
    def bot_data(self) -> dict[str, str | Numbers]:
        return classproperty.bot_data_

    @bot_data.setter
    def bot_data(self, new_botdata: dict[str, str | Numbers]) -> None:
        classproperty.bot_data_ = new_botdata

    @property
    def AuthBot(self):  # pragma: no cover
        from .Utils.auth import AuthBot

        return AuthBot()

    @property
    def SearchBot(self):  # pragma: no cover

        from .Utils.search import SeachBot

        return SeachBot()

    @property
    def interact(self):  # pragma: no cover
        from .Utils.interator import Interact

        return Interact()

    @property
    def printtext(self):  # pragma: no cover
        from .Utils.PrintLogs import printbot

        return printbot

    @property
    def MakeXlsx(self):  # pragma: no cover
        from .Utils.MakeTemplate import MakeXlsx

        return MakeXlsx

    @property
    def cities_Amazonas(self) -> Callable[[], dict[str, str]]:  # pragma: no cover
        from .Utils.dicionarios import cities_Amazonas

        return cities_Amazonas

    @property
    def elements(self):  # pragma: no cover
        from .Utils.elements import ElementsBot

        return ElementsBot().Elements

    @property
    def vara(self) -> str:  # pragma: no cover
        return classproperty.vara_

    @vara.setter
    def vara(self, vara_str: str) -> None:
        classproperty.vara_ = vara_str

    @property
    def path_accepted(self) -> str:
        return classproperty.path_accepted_

    @path_accepted.setter
    def path_accepted(self, new_path: str) -> None:
        classproperty.path_accepted_ = new_path
