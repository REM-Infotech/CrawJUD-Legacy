from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Type, Union

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
Typebot: Type[str]


class PropertiesCrawJUD:

    load_dotenv()

    name_cert_ = ""
    path_erro_: Type[str] = ""
    OpenAI_ = OpenAI()
    appends_: List[str] = []
    another_append_: List[str] = []
    path_args_: Type[str] = ""
    path_accepted_: Type[str] = ""
    vara_: Type[str] = ""
    systembot: Type[str] = str("")
    state_or_client_: Type[str] = ""
    type_log_: Type[str] = "info"
    message_: Type[str] = ""
    pid_: Type[str] = ""
    kwrgs_: Dict[str, Union[TypeValues, SubDict]] = {}
    row_: Type[int] = 0
    message_error_: Type[str] = ""
    bot_data_: Dict[str, Union[TypeValues, SubDict]] = {}
    graphicMode_: Type[str] = "doughnut"
    out_dir: Type[str] = ""
    user_data_dir: Type[str] = ""
    cr_list_args: list[str] = []
    drv: Type[WebDriver] = ""
    wt: Type[WebDriverWait] = ""
    path_: Path = ""
    state_: Type[str] = ""

    @property
    def path(self) -> Path:
        return self.path_

    @path.setter
    def path(self, new_path: Path) -> None:

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.path_ = new_path

    @property
    def path_args(self) -> Type[str]:
        return self.path_args_

    @path_args.setter
    def path_args(self, new_path: Type[str]) -> None:
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
    def system(self) -> Type[str]:
        return self.systembot

    @system.setter
    def system(self, systembot: Type[str]) -> None:
        self.systembot = systembot

    @property
    def state_or_client(self) -> Type[str]:
        return self.state_or_client_

    @state_or_client.setter
    def state_or_client(self, new_s: Type[str]) -> None:
        self.state_or_client_ = new_s

    @property
    def type_log(self) -> Type[str]:
        return self.type_log_

    @type_log.setter
    def type_log(self, new_log: Type[str]) -> None:
        self.type_log_ = new_log

    @property
    def pid(self) -> Type[str]:
        return self.pid_

    @pid.setter
    def pid(self, pid_: Type[str]) -> None:
        self.pid_ = pid_

    @property
    def message(self) -> Type[str]:
        return self.message

    @message.setter
    def message(self, new_msg: Type[str]) -> None:
        self.message_bot = new_msg

    @property
    def driver(self) -> WebDriver:
        return self.drv

    @driver.setter
    def driver(self, new_drv: WebDriver) -> None:
        self.drv = new_drv

    @property
    def wait(self) -> WebDriverWait:
        return self.wt

    @wait.setter
    def wait(self, new_wt: WebDriverWait) -> None:
        self.wt = new_wt

    @property
    def chr_dir(self) -> Type[str]:
        return self.user_data_dir

    @chr_dir.setter
    def chr_dir(self, new_dir: Type[str]) -> None:
        self.user_data_dir = new_dir

    @property
    def output_dir_path(self) -> Type[str]:
        return self.out_dir

    @output_dir_path.setter
    def output_dir_path(self, new_outdir: Type[str]) -> None:
        self.out_dir = new_outdir

    @property
    def kwrgs(self) -> Dict[str, TypeValues | SubDict]:
        return self.kwrgs_

    @kwrgs.setter
    def kwrgs(self, new_kwg: Dict[str, Any]) -> None:
        self.kwrgs_ = new_kwg

        for key, value in list(new_kwg.items()):
            setattr(self, key, value)

    @property
    def row(self) -> Type[int]:
        return self.row_

    @row.setter
    def row(self, new_row: int) -> None:
        self.row_ = new_row

    @property
    def message_error(self) -> Type[str]:
        return self.message_boterror_

    @message_error.setter
    def message_error(self, nw_m: Type[str]) -> Type[str]:
        self.message_boterror_ = nw_m

    @property
    def graphicMode(self) -> Type[str]:
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
    def vara(self) -> Type[str]:
        return self.vara_

    @vara.setter
    def vara(self, vara_str: Type[str]) -> None:
        self.vara_ = vara_str

    @property
    def path_accepted(self) -> Type[str]:
        return self.path_accepted_

    @path_accepted.setter
    def path_accepted(self, new_path: Type[str]) -> None:
        self.path_accepted_ = new_path

    @property
    def OpenAI_client(self) -> OpenAI:
        return self.OpenAI_

    @property
    def typebot(self) -> Type[str]:
        return self.type_bot

    @typebot.setter
    def typebot(self, type_bot: str) -> None:
        self.type_bot = type_bot

    @property
    def state(self) -> Type[str]:
        return self.state_

    @state.setter
    def state(self, state_: str) -> None:
        self.state_ = state_

    @property
    def path_erro(self) -> Type[str]:
        return self.path_erro_

    @path_erro.setter
    def path_erro(self, path_erro_: str):
        self.path_erro_ = path_erro_

    @property
    def name_cert(self) -> Type[str]:
        return self.name_cert_

    @name_cert.setter
    def name_cert(self, name_cert: str) -> None:
        self.name_cert_ = name_cert


# class PropertiesCrawJUD(PropertiesCrawJUD):
#     def __init__(self, *args, **kwargs) -> None:
#         self.__dict__.update(kwargs)
#         self.kwrgs = kwargs

#     def __getattr__(self, nome: Type[str]) -> TypeHint:
#         super_cls = super()
#         item = self.kwrgs.get(nome, None)

#         if not item:
#             item = getattr(super_cls, nome, None)

#         return item
