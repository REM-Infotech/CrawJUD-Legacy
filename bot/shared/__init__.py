from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union, get_type_hints

from dotenv_vault import load_dotenv
from pydantic import BaseModel, ValidationError
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from .. import OpenAI

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = Dict[str, Union[TypeValues, Numbers]]

load_dotenv()

TypeHint = Union[List[str | Numbers | SubDict] | SubDict]


class CustomProperty(property):
    def __set__(self, obj, value) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")

        try:
            self.type_ = get_type_hints(self.fget).get("return")
            self.validate_type(value)
        except ValidationError as e:
            raise TypeError(f"Invalid value: {e}")

        self.fget(obj)
        self.fset(obj, value)

    def validate_type(self, value) -> None:
        """
        Valida o tipo do valor usando Pydantic.
        """

        class TypedPropertyModel(BaseModel):
            value: self.type_

            class Config:
                arbitrary_types_allowed = True

        TypedPropertyModel(value=value)


class PropertiesCrawJUD:
    load_dotenv()

    row_: int = 0
    pid_: str = None
    vara_: str = None
    state_: str = None
    client_: str = None
    message_: str = None
    type_bot: str = None
    name_cert_: str = None
    systembot_: str = None
    message_error_: str = None
    state_or_client_: str = None
    type_log_: str = str("info")
    graphicMode_: str = str("doughnut")

    _start_time_ = 0.0

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
    bot_data_: Dict[str, TypeValues | SubDict] = {}

    @CustomProperty
    def start_time(self) -> float | int:
        return self._start_time_

    @start_time.setter
    def start_time(self, start_time: int | float) -> None:
        self._start_time_ = start_time

    @CustomProperty
    def path(self) -> Path:
        return PropertiesCrawJUD.path_

    @path.setter
    def path(self, new_var: Path) -> None:
        PropertiesCrawJUD.path_ = new_var

    @CustomProperty
    def path_args(self) -> Path:
        return PropertiesCrawJUD.path_args_

    @path_args.setter
    def path_args(self, new_var: Path) -> None:
        PropertiesCrawJUD.path_args_ = new_var

    @CustomProperty
    def appends(self) -> List[str]:
        return PropertiesCrawJUD.appends_

    @appends.setter
    def appends(self, new_var: List) -> None:
        PropertiesCrawJUD.appends_ = new_var

    @CustomProperty
    def another_append(self) -> List[str]:
        return PropertiesCrawJUD.another_append_

    @another_append.setter
    def another_append(self, new_var: list) -> None:
        PropertiesCrawJUD.another_append_ = new_var

    @CustomProperty
    def system(self) -> str:
        return PropertiesCrawJUD.systembot_

    @system.setter
    def system(self, systembot_) -> None:
        PropertiesCrawJUD.systembot_ = systembot_

    @CustomProperty
    def state_or_client(self) -> str:
        return PropertiesCrawJUD.state_or_client_

    @state_or_client.setter
    def state_or_client(self, new_var: str) -> None:
        PropertiesCrawJUD.state_or_client_ = new_var

    @CustomProperty
    def type_log(self) -> str:
        return PropertiesCrawJUD.type_log_

    @type_log.setter
    def type_log(self, new_var: str) -> None:
        PropertiesCrawJUD.type_log_ = new_var

    @CustomProperty
    def pid(self) -> str:
        return PropertiesCrawJUD.pid_

    @pid.setter
    def pid(self, pid_) -> None:
        PropertiesCrawJUD.pid_ = pid_

    @CustomProperty
    def message(self) -> str:
        return PropertiesCrawJUD.message_

    @message.setter
    def message(self, new_msg: str) -> None:
        PropertiesCrawJUD.message_ = new_msg

    @CustomProperty
    def driver(self) -> WebDriver:
        return PropertiesCrawJUD.driver_

    @driver.setter
    def driver(self, new_driver_: WebDriver) -> None:
        PropertiesCrawJUD.driver_ = new_driver_

    @CustomProperty
    def wait(self) -> WebDriverWait:
        return PropertiesCrawJUD.webdriverwait_

    @wait.setter
    def wait(self, new_webdriverwait_: WebDriverWait) -> None:
        PropertiesCrawJUD.webdriverwait_ = new_webdriverwait_

    @CustomProperty
    def chr_dir(self) -> Path:
        return PropertiesCrawJUD.user_data_dir

    @chr_dir.setter
    def chr_dir(self, new_path: Path) -> None:
        PropertiesCrawJUD.user_data_dir = new_path

    @CustomProperty
    def output_dir_path(self) -> Path:
        return PropertiesCrawJUD.out_dir

    @output_dir_path.setter
    def output_dir_path(self, new_path: Path) -> None:
        PropertiesCrawJUD.out_dir = new_path

    @CustomProperty(type_=Dict[str, TypeValues | SubDict])
    def kwrgs(self) -> Dict[str, TypeValues | SubDict]:
        return PropertiesCrawJUD.kwrgs_

    @kwrgs.setter
    def kwrgs(self, new_kwg: Dict[str, Any]) -> None:
        PropertiesCrawJUD.kwrgs_ = new_kwg

    @CustomProperty(type_=int)
    def row(self) -> int:
        return PropertiesCrawJUD.row_

    @row.setter
    def row(self, new_row: int) -> None:
        PropertiesCrawJUD.row_ = new_row

    @CustomProperty
    def message_error(self) -> str:
        return PropertiesCrawJUD.message_error_

    @message_error.setter
    def message_error(self, nw_m) -> str:
        PropertiesCrawJUD.message_error_ = nw_m

    @CustomProperty
    def graphicMode(self) -> str:
        return PropertiesCrawJUD.graphicMode_

    @graphicMode.setter
    def graphicMode(self, new_graph) -> None:
        PropertiesCrawJUD.graphicMode_ = new_graph

    @CustomProperty(type_=Dict[str, TypeValues | SubDict])
    def bot_data(self) -> Dict[str, TypeValues | SubDict]:
        return PropertiesCrawJUD.bot_data_

    @bot_data.setter
    def bot_data(self, new_botdata: Dict[str, TypeValues | SubDict]) -> None:
        PropertiesCrawJUD.bot_data_ = new_botdata

    @CustomProperty
    def vara(self) -> str:
        return PropertiesCrawJUD.vara_

    @vara.setter
    def vara(self, vara_str) -> None:
        PropertiesCrawJUD.vara_ = vara_str

    @CustomProperty
    def path_accepted(self) -> Path:
        return PropertiesCrawJUD.path_accepted_

    @path_accepted.setter
    def path_accepted(self, new_path) -> None:
        PropertiesCrawJUD.path_accepted_ = new_path

    @CustomProperty(type_=OpenAI)
    def OpenAI_client(self) -> OpenAI:
        load_dotenv()

        return OpenAI()

    @CustomProperty
    def typebot(self) -> str:
        return PropertiesCrawJUD.type_bot

    @typebot.setter
    def typebot(self, type_bot) -> None:
        PropertiesCrawJUD.type_bot = type_bot

    @CustomProperty
    def state(self) -> str:
        return PropertiesCrawJUD.state_

    @state.setter
    def state(self, state_: str) -> None:
        PropertiesCrawJUD.state_ = state_

    @CustomProperty
    def path_erro(self) -> Path:
        return PropertiesCrawJUD.path_erro_

    @path_erro.setter
    def path_erro(self, new_path: Path) -> None:
        PropertiesCrawJUD.path_erro_ = new_path

    @CustomProperty
    def name_cert(self) -> str:
        return PropertiesCrawJUD.name_cert_

    @name_cert.setter
    def name_cert(self, name_cert) -> None:
        PropertiesCrawJUD.name_cert_ = name_cert

    @CustomProperty
    def client(self) -> str:
        return PropertiesCrawJUD.client_

    @client.setter
    def client(self, client_) -> None:
        PropertiesCrawJUD.client_ = client_

    # Funcionalidades
    @CustomProperty
    def AuthBot(self) -> Callable[[], bool]:
        from ..Utils import AuthBot as _AuthBot_

        return _AuthBot_().auth

    @CustomProperty
    def MakeXlsx(self) -> _MakeXlsx_:
        from ..Utils import MakeXlsx as _MakeXlsx_

        return _MakeXlsx_()

    @CustomProperty
    def Interact(self) -> _Interact_:
        from ..Utils import Interact as _Interact_

        return _Interact_()

    @CustomProperty
    def PrintBot(self) -> _PrintBot_:
        from ..Utils import PrintBot as _PrintBot_

        return _PrintBot_()

    @CustomProperty
    def SearchBot(self) -> _SearchBot_:
        from ..Utils import SearchBot as _SearchBot_

        return _SearchBot_()

    @CustomProperty
    def OtherUtils(self) -> _OtherUtils_:
        from ..Utils import OtherUtils as _OtherUtils_

        return _OtherUtils_()

    @CustomProperty
    def elements(self) -> Union[ESAJ_AM, ELAW_AME, PJE_AM, PROJUDI_AM]:
        from ..Utils import ElementsBot as _ElementsBot_

        return _ElementsBot_().Config().Elements

    @CustomProperty
    def DriverLaunch(self) -> Callable[..., Tuple[WebDriver, WebDriverWait]]:
        from ..Utils import DriverBot as _DriverBot_

        return _DriverBot_().DriverLaunch

    @CustomProperty
    def search_bot(self) -> Callable[[], bool]:
        return self.SearchBot.search_

    @CustomProperty
    def dataFrame(self) -> Callable[[], list[dict[str, str]]]:
        return self.OtherUtils.dataFrame

    @CustomProperty(type_=bool)
    def isStoped(self) -> bool:
        stopped = Path(self.output_dir_path).joinpath(f"{self.pid}.flag").exists()
        return stopped

    @CustomProperty
    def elawFormats(self) -> Callable[..., dict[str, str]]:
        return self.OtherUtils.elawFormats

    @CustomProperty
    def calc_time(self) -> Callable[[], list]:
        return self.OtherUtils.calc_time

    @CustomProperty
    def append_moves(self) -> Callable[[], None]:
        return self.OtherUtils().append_moves

    @CustomProperty
    def append_success(self) -> Callable[..., None]:
        return self.OtherUtils.append_success

    @CustomProperty
    def append_error(self) -> Callable[..., None]:
        return self.OtherUtils.append_error

    @CustomProperty
    def append_validarcampos(self) -> Callable[..., None]:
        return self.OtherUtils.append_validarcampos

    @CustomProperty
    def count_doc(self) -> Callable[..., str | None]:
        return self.OtherUtils.count_doc

    @CustomProperty
    def get_recent(self) -> Callable[..., str | None]:
        return self.OtherUtils.get_recent

    @CustomProperty
    def format_String(self) -> Callable[..., str]:
        return self.OtherUtils.format_String

    @CustomProperty
    def normalizar_nome(self) -> Callable[..., str]:
        return self.OtherUtils.normalizar_nome

    @CustomProperty
    def similaridade(self) -> Callable[..., float]:
        return self.OtherUtils.similaridade

    @CustomProperty
    def finalize_execution(self) -> Callable[[], None]:
        return self.OtherUtils.finalize_execution

    @CustomProperty
    def install_cert(self) -> Callable[[], None]:
        return self.OtherUtils.install_cert

    @CustomProperty
    def group_date_all(self) -> Callable[..., list[dict[str, str]]]:
        return self.OtherUtils.group_date_all

    @CustomProperty
    def group_keys(self) -> Callable[..., dict[str, str]]:
        return self.OtherUtils.group_keys

    @CustomProperty
    def gpt_chat(self) -> Callable[..., str]:
        """
        Analyzes a given legal document text and adjusts the response based on the type of document.
        This method uses the OpenAI GPT model to analyze the provided text and generate a response
        that identifies the type of legal document and extracts relevant information based on the
        document type. The document types include sentences, initial petitions, defenses, and
        interlocutory decisions.
        Args:
            text_mov (str): The text of the legal document to be analyzed.
        Returns:
            str: The adjusted response based on the type of document, including extracted values
                 and summaries as specified in the system message.
        Raises:
            Exception: If an error occurs during the API call or processing.
        """

        return self.OtherUtils.gpt_chat

    @CustomProperty
    def text_is_a_date(self) -> Callable[..., bool]:
        return self.OtherUtils.text_is_a_date


if __name__ == "__main__":
    from ..Utils import ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM
    from ..Utils import Interact as _Interact_
    from ..Utils import MakeXlsx as _MakeXlsx_
    from ..Utils import OtherUtils as _OtherUtils_
    from ..Utils import PrintBot as _PrintBot_
    from ..Utils import SearchBot as _SearchBot_
