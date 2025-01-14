from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, Union

from dotenv import load_dotenv
from memory_profiler import profile
from openai import OpenAI
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = Dict[str, Union[TypeValues, Numbers]]

fp = open("memory_profiler_classproperty.log", "+w")


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
    @profile(stream=fp)
    def appends(self):
        return self.appends_

    @appends.setter
    @profile(stream=fp)
    def appends(self, new_appends: list):
        self.appends_ = new_appends

    @property
    @profile(stream=fp)
    def another_append(self):
        return self.another_append_

    @another_append.setter
    @profile(stream=fp)
    def another_append(self, new_another_append: list):
        self.another_append_ = new_another_append

    @property
    @profile(stream=fp)
    def OpenAI_client(self) -> OpenAI:

        return self.OpenAI_client_

    @property
    @profile(stream=fp)
    def system(self):
        return classproperty._system

    @system.setter
    @profile(stream=fp)
    def system(self, system_: str):
        classproperty._system = system_

    @property
    @profile(stream=fp)
    def state_or_client(self):
        return classproperty._state_or_client_

    @state_or_client.setter
    @profile(stream=fp)
    def state_or_client(self, new_s: str):
        classproperty._state_or_client_ = new_s

    @property
    @profile(stream=fp)
    def type_log(self):
        return classproperty._type_log

    @type_log.setter
    @profile(stream=fp)
    def type_log(self, new_log: str):
        classproperty._type_log = new_log

    @property
    @profile(stream=fp)
    def pid(self) -> int:
        return classproperty._pid

    @pid.setter
    @profile(stream=fp)
    def pid(self, pid_) -> int:
        classproperty._pid = pid_

    @property
    @profile(stream=fp)
    def message(self) -> str:
        return classproperty._message

    @message.setter
    @profile(stream=fp)
    def message(self, new_msg: str) -> str:
        classproperty._message = new_msg

    @property
    @profile(stream=fp)
    def isStoped(self):
        chk = os.path.exists(os.path.join(self.output_dir_path, f"{self.pid}.flag"))
        return chk

    @property
    @profile(stream=fp)
    def driver(self) -> WebDriver:  # pragma: no cover
        return classproperty.drv

    @driver.setter
    @profile(stream=fp)
    def driver(self, new_drv: WebDriver):  # pragma: no cover
        classproperty.drv = new_drv

    @property
    @profile(stream=fp)
    def wait(self) -> WebDriverWait:  # pragma: no cover
        return classproperty.wt

    @wait.setter
    @profile(stream=fp)
    def wait(self, new_wt: WebDriverWait):  # pragma: no cover
        classproperty.wt = new_wt

    @property
    @profile(stream=fp)
    def chr_dir(self):
        return classproperty.user_data_dir

    @chr_dir.setter
    @profile(stream=fp)
    def chr_dir(self, new_dir: str):
        classproperty.user_data_dir = new_dir

    @property
    @profile(stream=fp)
    def output_dir_path(self):
        return classproperty.out_dir

    @output_dir_path.setter
    @profile(stream=fp)
    def output_dir_path(self, new_outdir: str):
        classproperty.out_dir = new_outdir

    @property
    @profile(stream=fp)
    def kwrgs(self) -> dict:
        return classproperty.kwrgs_

    @kwrgs.setter
    @profile(stream=fp)
    def kwrgs(self, new_kwg):
        classproperty.kwrgs_ = new_kwg

    @property
    @profile(stream=fp)
    def row(self) -> int:
        return classproperty.row_

    @row.setter
    @profile(stream=fp)
    def row(self, new_row: int):
        classproperty.row_ = new_row

    @property
    @profile(stream=fp)
    def message_error(self) -> str:
        return classproperty.message_error_

    @message_error.setter
    @profile(stream=fp)
    def message_error(self, nw_m: str) -> str:
        classproperty.message_error_ = nw_m

    @property
    @profile(stream=fp)
    def graphicMode(self):
        return classproperty.graphicMode_

    @graphicMode.setter
    @profile(stream=fp)
    def graphicMode(self, new_graph):
        classproperty.graphicMode_ = new_graph

    @property
    @profile(stream=fp)
    def list_args(self):  # pragma: no cover
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
    @profile(stream=fp)
    def list_args(self, new_Args: list[str]):  # pragma: no cover
        classproperty.cr_list_args = new_Args

    @property
    @profile(stream=fp)
    def bot_data(self) -> dict[str, str | Numbers]:
        return classproperty.bot_data_

    @bot_data.setter
    @profile(stream=fp)
    def bot_data(self, new_botdata: dict[str, str | Numbers]):
        classproperty.bot_data_ = new_botdata

    @property
    @profile(stream=fp)
    def AuthBot(self):  # pragma: no cover
        from .Utils.auth import AuthBot

        return AuthBot()

    @property
    @profile(stream=fp)
    def SearchBot(self):  # pragma: no cover

        from .Utils.search import SeachBot

        return SeachBot()

    @property
    @profile(stream=fp)
    def interact(self):  # pragma: no cover
        from .Utils.interator import Interact

        return Interact()

    @property
    @profile(stream=fp)
    def printtext(self):  # pragma: no cover
        from .Utils.PrintLogs import printbot

        return printbot

    @property
    @profile(stream=fp)
    def MakeXlsx(self):  # pragma: no cover
        from .Utils.MakeTemplate import MakeXlsx

        return MakeXlsx

    @property
    @profile(stream=fp)
    def cities_Amazonas(self):  # pragma: no cover
        from .Utils.dicionarios import cities_Amazonas

        return cities_Amazonas

    @property
    @profile(stream=fp)
    def elements(self):  # pragma: no cover
        from .Utils.elements import ElementsBot

        return ElementsBot().Elements

    @property
    @profile(stream=fp)
    def vara(self) -> str:  # pragma: no cover
        return classproperty.vara_

    @vara.setter
    @profile(stream=fp)
    def vara(self, vara_str: str):
        classproperty.vara_ = vara_str

    @property
    @profile(stream=fp)
    def path_accepted(self):
        return classproperty.path_accepted_

    @path_accepted.setter
    @profile(stream=fp)
    def path_accepted(self, new_path: str):
        classproperty.path_accepted_ = new_path
