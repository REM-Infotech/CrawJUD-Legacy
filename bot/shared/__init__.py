from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Type, Union, Callable, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = Dict[str, Union[TypeValues, Numbers]]

# from memory_profiler import profile
# fp = open("memory_profiler_self.log", "+w")

load_dotenv()

TypeHint = Union[List[str | Numbers | SubDict] | SubDict]


class PropertiesCrawJUD:

    load_dotenv()

    OpenAI_ = OpenAI()

    row_: int = 0
    pid_: str = None
    vara_: str = None
    state_: str = None
    client_: str = None
    message_: str = None
    type_bot_: str = None
    name_cert_: str = None
    systembot_: str = None
    message_error_: str = None
    state_or_client_: str = None
    type_log_: str = str("info")
    graphicMode_: str = str("doughnut")

    path_: Path = None
    out_dir: Path = None
    path_erro_: Path = None
    path_args_: Path = None
    user_data_dir: Path = None
    path_accepted_: Path = None

    driver_: WebDriver = None
    webdriverwait_: WebDriverWait = None

    appends_: List[str] = []
    cr_list_args: List[str] = []
    another_append_: List[str] = []

    kwrgs_: Dict[str, Union[TypeValues, SubDict]] = {}
    bot_data_: Dict[str, Union[TypeValues, SubDict]] = {}

    @property
    def path(self) -> Path:
        return self.path_

    @path.setter
    def path(self, new_path: Path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.path_ = new_path

    @property
    def path_args(self) -> Path:
        return self.path_args_

    @path_args.setter
    def path_args(self, new_path: Path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.path_args_ = new_path

    @property
    def appends(self) -> List[str]:
        return self.appends_

    @appends.setter
    def appends(self, new_appends: list) -> None:
        self.appends_ = new_appends

    @property
    def another_append(self) -> List[str]:
        return self.another_append_

    @another_append.setter
    def another_append(self, new_another_append: list) -> None:
        self.another_append_ = new_another_append

    @property
    def system(self) -> str:
        return self.systembot_

    @system.setter
    def system(self, systembot_) -> None:
        self.systembot_ = systembot_

    @property
    def state_or_client(self) -> str:
        return self.state_or_client_

    @state_or_client.setter
    def state_or_client(self, new_s) -> None:
        self.state_or_client_ = new_s

    @property
    def type_log(self) -> str:
        return self.type_log_

    @type_log.setter
    def type_log(self, new_log) -> None:
        self.type_log_ = new_log

    @property
    def pid(self) -> str:
        return self.pid_

    @pid.setter
    def pid(self, pid_) -> None:
        self.pid_ = pid_

    @property
    def message(self) -> str:
        return self.message_

    @message.setter
    def message(self, new_msg) -> None:
        self.message_bot = new_msg

    @property
    def driver(self) -> WebDriver:
        return self.driver_

    @driver.setter
    def driver(self, new_driver_: WebDriver) -> None:
        self.driver_ = new_driver_

    @property
    def wait(self) -> WebDriverWait:
        return self.webdriverwait_

    @wait.setter
    def wait(self, new_webdriverwait_: WebDriverWait) -> None:
        self.webdriverwait_ = new_webdriverwait_

    @property
    def chr_dir(self) -> Path:
        return self.user_data_dir

    @chr_dir.setter
    def chr_dir(self, new_path: Path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.user_data_dir = new_path

    @property
    def output_dir_path(self) -> Path:
        return self.out_dir

    @output_dir_path.setter
    def output_dir_path(self, new_path: Path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.out_dir = new_path

    @property
    def kwrgs(self) -> Dict[str, TypeValues | SubDict]:
        return self.kwrgs_

    @kwrgs.setter
    def kwrgs(self, new_kwg: Dict[str, Any]) -> None:
        self.kwrgs_ = new_kwg

    @property
    def row(self) -> Type[int]:
        return self.row_

    @row.setter
    def row(self, new_row: int) -> None:
        self.row_ = new_row

    @property
    def message_error(self) -> str:
        return self.message_error_

    @message_error.setter
    def message_error(self, nw_m) -> str:
        self.message_error_ = nw_m

    @property
    def graphicMode(self) -> str:
        return self.graphicMode_

    @graphicMode.setter
    def graphicMode(self, new_graph) -> None:
        self.graphicMode_ = new_graph

    @property
    def bot_data(self) -> dict[str, str | Numbers]:
        return self.bot_data_

    @bot_data.setter
    def bot_data(self, new_botdata: dict[str, str | Numbers]) -> None:
        self.bot_data_ = new_botdata

    @property
    def vara(self) -> str:
        return self.vara_

    @vara.setter
    def vara(self, vara_str) -> None:
        self.vara_ = vara_str

    @property
    def path_accepted(self) -> Path:
        return self.path_accepted_

    @path_accepted.setter
    def path_accepted(self, new_path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.path_accepted_ = new_path

    @property
    def OpenAI_client(self) -> OpenAI:
        return self.OpenAI_

    @property
    def typebot(self) -> str:
        return self.type_bot

    @typebot.setter
    def typebot(self, type_bot) -> None:
        self.type_bot = type_bot

    @property
    def state(self) -> str:
        return self.state_

    @state.setter
    def state(self, state_: str) -> None:
        self.state_ = state_

    @property
    def path_erro(self) -> Path:

        return self.path_erro_

    @path_erro.setter
    def path_erro(self, new_path: Path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.path_erro_ = new_path

    @property
    def name_cert(self) -> str:
        return self.name_cert_

    @name_cert.setter
    def name_cert(self, name_cert) -> None:
        self.name_cert_ = name_cert

    @property
    def client(self) -> str:
        return self.client_

    @client.setter
    def client(self, client_) -> None:
        self.client_ = client_

    @property
    def AuthBot(self) -> Callable[[], bool]:

        from ..Utils import AuthBot as _AuthBot_

        return _AuthBot_().auth

    @property
    def MakeXlsx(self) -> _MakeXlsx_:

        from ..Utils import MakeXlsx as _MakeXlsx_

        return _MakeXlsx_()

    @property
    def Interact(self) -> _Interact_:

        from ..Utils import Interact as _Interact_

        return _Interact_()

    @property
    def PrintBot(self) -> _PrintBot_:

        from ..Utils import PrintBot as _PrintBot_

        return _PrintBot_()

    @property
    def SearchBot(self) -> _SearchBot_:

        from ..Utils import SearchBot as _SearchBot_

        return _SearchBot_()

    @property
    def OtherUtils(self) -> _OtherUtils_:

        from ..Utils import OtherUtils as _OtherUtils_

        return _OtherUtils_()

    @property
    def elements(self) -> Union[ESAJ_AM, ELAW_AME, PJE_AM, PROJUDI_AM]:

        from ..Utils import ElementsBot as _ElementsBot_

        return _ElementsBot_().Config().Elements

    @property
    def DriverLaunch(self) -> Callable[..., Tuple[WebDriver, WebDriverWait]]:

        from ..Utils import DriverBot as _DriverBot_

        return _DriverBot_().DriverLaunch

    def search_bot(self) -> bool:

        return self.SearchBot_.search_()

    @property
    def append_error(self) -> Callable[..., None]:

        return self.OtherUtils.append_error

    @property
    def append_success(self) -> Callable[..., None]:

        return self.OtherUtils.append_success

    @property
    def dataFrame(self) -> Callable[[], list[dict[str, str]]]:

        return self.OtherUtils.dataFrame

    @property
    def isStoped(self) -> bool:

        file_check = Path(self.output_dir_path).joinpath(f"{self.pid}.flag").resolve()
        return file_check.exists()


if __name__ == "__main__":
    from ..Utils import (
        PrintBot as _PrintBot_,
        Interact as _Interact_,
        OtherUtils as _OtherUtils_,
        SearchBot as _SearchBot_,
        MakeXlsx as _MakeXlsx_,
        ELAW_AME,
        ESAJ_AM,
        PJE_AM,
        PROJUDI_AM,
    )
