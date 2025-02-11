"""Shared utilities and configuration for the CrawJUD-Bots application.

This module defines shared properties and utilities used across the CrawJUD-Bots
application, including configuration for paths, WebDriver instances, and bot settings.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    LiteralString,
    Union,
)

from dotenv_vault import load_dotenv
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from socketio import Client

from utils import init_log

from .. import OpenAI

if TYPE_CHECKING:
    from ..Utils import ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM
    from ..Utils import ElementsBot as ElementsBot_
    from ..Utils import Interact as _Interact_
    from ..Utils import MakeXlsx as _MakeXlsx_
    from ..Utils import OtherUtils as _OtherUtils_
    from ..Utils import PrintBot as _PrintBot_
    from ..Utils import SearchBot as _SearchBot_

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = dict[str, Union[TypeValues, Numbers]]

load_dotenv()

TypeHint = Union[list[str | Numbers | SubDict] | SubDict]


class PropertiesCrawJUD:
    """Configuration and state holder for the CrawJUD bot.

    This class provides properties to manage configuration and state of the CrawJUD bot,
    including paths, WebDriver instances, and various runtime parameters.

    Attributes:
        row_ (int): Current row index.
        pid_ (str): Process ID.
        vara_ (str): Variable A.
        state_ (str): Current state.
        client_ (str): Client information.
        message_ (str): Current message.
        type_bot (str): type of bot.
        name_cert_ (str): Certificate name.
        systembot_ (str): System bot identifier.
        message_error_ (str): Error message.
        state_or_client_ (str): State or client identifier.
        type_log_ (str): type of log (default "info").
        graphicMode_ (str): Mode of graphics (default "doughnut").
        # ...other attributes...

    """

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
    type_log_: str = "info"
    graphicMode_: str = "doughnut"  # noqa: N815
    name_colunas_: list[str] = None
    _start_time_ = 0.0
    _connected = False
    _AuthBot_ = None
    _DriverBot_ = None
    _ElementsBot_ = None
    Interact_ = None
    MakeXlsx_ = None
    OtherUtils_ = None
    PrintBot_ = None
    SearchBot_ = None
    ElementsBotConfig_ = None
    path_: Path = None
    out_dir: Path = None
    path_erro_: Path = None
    path_args_: Path = None
    user_data_dir: Path = None
    path_accepted_: Path = None

    driver_: WebDriver = None
    webdriverwait_: WebDriverWait = None

    appends_: list[str] = []
    cr_list_args: list[str] = []
    another_append_: list[str] = []

    kwargs_: dict[str, Union[TypeValues, SubDict]] = {}
    bot_data_: dict[str, TypeValues | SubDict] = {}

    # sio = SimpleClient
    sio = Client(reconnection_attempts=5)
    logger = init_log()

    @sio.on("connect", namespace="*")
    @staticmethod
    def on_connect(event: any = None, namespace: str = None, client_: str = None) -> None:
        """Handle the connect event."""

    @sio.on("disconnect", namespace="*")
    @staticmethod
    def on_disconnect(event: any = None, namespace: str = None, client_: str = None) -> None:
        """Handle the disconnect event."""

    @sio.on("log_message", namespace="*")
    @staticmethod
    def on_message(event: any = None, data: dict = None, namespace: str = None, client_: str = None) -> None:
        """Handle the log_message event."""

    @sio.on("stop_bot", namespace="*")
    @staticmethod
    def on_stop_bot(event: any = None, data: dict = None, namespace: str = None, client_: str = None) -> None:
        """Handle the stop_bot event."""

    @property
    def connected(self) -> bool:
        """Return the connection status."""
        return PropertiesCrawJUD.connected

    @connected.setter
    def connected(self, status: bool) -> None:
        """Set the connection status.

        Args:
            status (bool): The new connection status.

        """
        PropertiesCrawJUD.connected = status

    def __init__(self) -> None:
        """Initialize the PropertiesCrawJUD instance."""
        from ..Utils import AuthBot as _AuthBot_
        from ..Utils import DriverBot as _DriverBot_
        from ..Utils import ElementsBot as _ElementsBot_
        from ..Utils import Interact as _Interact_
        from ..Utils import MakeXlsx as _MakeXlsx_
        from ..Utils import OtherUtils as _OtherUtils_
        from ..Utils import PrintBot as _PrintBot_
        from ..Utils import SearchBot as _SearchBot_

        PropertiesCrawJUD.OtherUtils_ = _OtherUtils_()
        PropertiesCrawJUD.SearchBot_ = _SearchBot_()
        PropertiesCrawJUD.Interact_ = _Interact_()
        PropertiesCrawJUD.MakeXlsx_ = _MakeXlsx_()
        PropertiesCrawJUD.AuthBot_ = _AuthBot_()
        PropertiesCrawJUD.OtherUtils_ = _OtherUtils_()
        PropertiesCrawJUD.ElementsBot_ = _ElementsBot_()
        PropertiesCrawJUD.PrintBot_ = _PrintBot_()
        PropertiesCrawJUD.DriverBot_ = _DriverBot_()

    def prt(self) -> None:
        """Print a message using the PrintBot's print_msg method.

        This method invokes the print_msg method of the PrintBot instance
        to display messages.

        """
        print_bot = getattr(PropertiesCrawJUD, "PrintBot_", None)
        if print_bot is None:
            from ..Utils import PrintBot as _PrintBot_

            self.PrintBot = _PrintBot_()
            PropertiesCrawJUD.PrintBot_ = self.PrintBot
        self.PrintBot.print_msg()

    def end_prt(self, status: str) -> None:
        """End the print session with the given status.

        Args:
            status (str): The status message to indicate the end of the print session.

        """
        self.PrintBot.end_prt(status)

    @property
    def PrintBot(self) -> _PrintBot_:  # noqa: N802
        """Return the PrintBot instance."""
        return PropertiesCrawJUD.PrintBot_

    @PrintBot.setter
    def PrintBot(self, new_var: _PrintBot_) -> None:  # noqa: N802
        """Set the PrintBot instance.

        Args:
            new_var (_PrintBot_): The new PrintBot instance.

        """
        PropertiesCrawJUD.PrintBot_ = new_var

    @property
    def start_time(self) -> float | int:
        """Return the start time."""
        return PropertiesCrawJUD.start_time_

    @start_time.setter
    def start_time(self, start_time: float) -> None:
        """Set the start time.

        Args:
            start_time (int | float): The start time value.

        """
        PropertiesCrawJUD.start_time_ = start_time

    @property
    def path(self) -> Path:
        """Return the current path."""
        return PropertiesCrawJUD.path_

    @path.setter
    def path(self, new_var: Path) -> None:
        """Set a new path.

        Args:
            new_var (Path): The new path value.

        """
        PropertiesCrawJUD.path_ = new_var

    @property
    def path_args(self) -> Path:
        """Return the path arguments."""
        return PropertiesCrawJUD.path_args_

    @path_args.setter
    def path_args(self, new_var: Path) -> None:
        """Set new path arguments.

        Args:
            new_var (Path): The new path arguments value.

        """
        PropertiesCrawJUD.path_args_ = new_var

    @property
    def appends(self) -> list[str]:
        """Return the list of appends."""
        return PropertiesCrawJUD.appends_

    @appends.setter
    def appends(self, new_var: list) -> None:
        """Set a new list of appends.

        Args:
            new_var (list): The new list of appends.

        """
        PropertiesCrawJUD.appends_ = new_var

    @property
    def another_append(self) -> list[str]:
        """Return another list of appends."""
        return PropertiesCrawJUD.another_append_

    @another_append.setter
    def another_append(self, new_var: list) -> None:
        """Set another list of appends.

        Args:
            new_var (list): The new list of appends.

        """
        PropertiesCrawJUD.another_append_ = new_var

    @property
    def system(self) -> str:
        """Return the system bot identifier."""
        return PropertiesCrawJUD.systembot_

    @system.setter
    def system(self, systembot_: str) -> None:
        """Set the system bot identifier.

        Args:
            systembot_ (str): The new system bot identifier.

        """
        PropertiesCrawJUD.systembot_ = systembot_

    @property
    def state_or_client(self) -> str:
        """Return the state or client identifier."""
        return PropertiesCrawJUD.state_or_client_

    @state_or_client.setter
    def state_or_client(self, new_var: str) -> None:
        """Set the state or client identifier.

        Args:
            new_var (str): The new state or client identifier.

        """
        PropertiesCrawJUD.state_or_client_ = new_var

    @property
    def type_log(self) -> str:
        """Return the type of log."""
        return PropertiesCrawJUD.type_log_

    @type_log.setter
    def type_log(self, new_var: str) -> None:
        """Set the type of log.

        Args:
            new_var (str): The new type of log.

        """
        PropertiesCrawJUD.type_log_ = new_var

    @property
    def pid(self) -> str:
        """Return the process ID."""
        return PropertiesCrawJUD.pid_

    @pid.setter
    def pid(self, pid_: str) -> None:
        """Set the process ID.

        Args:
            pid_ (str): The new process ID.

        """
        PropertiesCrawJUD.pid_ = pid_

    @property
    def message(self) -> str:
        """Return the current message."""
        return PropertiesCrawJUD.message_

    @message.setter
    def message(self, new_msg: str) -> None:
        """Set the current message.

        Args:
            new_msg (str): The new message.

        """
        PropertiesCrawJUD.message_ = new_msg

    @property
    def driver(self) -> WebDriver:
        """Return the WebDriver instance."""
        return PropertiesCrawJUD.driver_

    @driver.setter
    def driver(self, new_driver_: WebDriver) -> None:
        """Set the WebDriver instance.

        Args:
            new_driver_ (WebDriver): The new WebDriver instance.

        """
        PropertiesCrawJUD.driver_ = new_driver_

    @property
    def wait(self) -> WebDriverWait:
        """Return the WebDriverWait instance."""
        return PropertiesCrawJUD.webdriverwait_

    @wait.setter
    def wait(self, new_webdriverwait_: WebDriverWait) -> None:
        """Set the WebDriverWait instance.

        Args:
            new_webdriverwait_ (WebDriverWait): The new WebDriverWait instance.

        """
        PropertiesCrawJUD.webdriverwait_ = new_webdriverwait_

    @property
    def chr_dir(self) -> Path:
        """Return the user data directory path."""
        return PropertiesCrawJUD.user_data_dir

    @chr_dir.setter
    def chr_dir(self, new_path: Path) -> None:
        """Set the user data directory path.

        Args:
            new_path (Path): The new user data directory path.

        """
        PropertiesCrawJUD.user_data_dir = new_path

    @property
    def output_dir_path(self) -> Path:
        """Return the output directory path."""
        return PropertiesCrawJUD.out_dir

    @output_dir_path.setter
    def output_dir_path(self, new_path: Path) -> None:
        """Set the output directory path.

        Args:
            new_path (Path): The new output directory path.

        """
        PropertiesCrawJUD.out_dir = new_path

    @property
    def kwargs(self) -> dict[str, TypeValues | SubDict]:
        """Return the keyword arguments."""
        return PropertiesCrawJUD.kwargs_

    @kwargs.setter
    def kwargs(self, new_kwg: dict[str, any]) -> None:
        """Set the keyword arguments.

        Args:
            new_kwg (dict[str, any]): The new keyword arguments.

        """
        PropertiesCrawJUD.kwargs_ = new_kwg

    @property
    def row(self) -> int:
        """Return the current row index."""
        return PropertiesCrawJUD.row_

    @row.setter
    def row(self, new_row: int) -> None:
        """Set the current row index.

        Args:
            new_row (int): The new row index.

        """
        PropertiesCrawJUD.row_ = new_row

    @property
    def message_error(self) -> str:
        """Return the error message."""
        return PropertiesCrawJUD.message_error_

    @message_error.setter
    def message_error(self, nw_m: str) -> str:
        """Set the error message.

        Args:
            nw_m (str): The new error message.

        """
        PropertiesCrawJUD.message_error_ = nw_m

    @property
    def graphicMode(self) -> str:  # noqa: N802
        """Return the graphic mode."""
        return PropertiesCrawJUD.graphicMode_

    @graphicMode.setter
    def graphicMode(self, new_graph: str) -> None:  # noqa: N802
        """Set the graphic mode.

        Args:
            new_graph (str): The new graphic mode.

        """
        PropertiesCrawJUD.graphicMode_ = new_graph

    @property
    def bot_data(self) -> dict[str, TypeValues | SubDict]:
        """Return the bot data."""
        return PropertiesCrawJUD.bot_data_

    @bot_data.setter
    def bot_data(self, new_botdata: dict[str, TypeValues | SubDict]) -> None:
        """Set the bot data.

        Args:
            new_botdata (dict[str, TypeValues | SubDict]): The new bot data.

        """
        PropertiesCrawJUD.bot_data_ = new_botdata

    @property
    def vara(self) -> str:
        """Return the variable A."""
        return PropertiesCrawJUD.vara_

    @vara.setter
    def vara(self, vara_str: str) -> None:
        """Set the variable A.

        Args:
            vara_str (str): The new variable A.

        """
        PropertiesCrawJUD.vara_ = vara_str

    @property
    def path_accepted(self) -> Path:
        """Return the accepted path."""
        return PropertiesCrawJUD.path_accepted_

    @path_accepted.setter
    def path_accepted(self, new_path: Path) -> None:
        """Set the accepted path.

        Args:
            new_path (Path): The new accepted path.

        """
        PropertiesCrawJUD.path_accepted_ = new_path

    @property
    def OpenAI_client(self) -> OpenAI:  # noqa: N802
        """Return the OpenAI client."""
        load_dotenv()

        return OpenAI()

    @property
    def headgpt(self) -> LiteralString:
        """Return the head_gpt value."""
        from .head_gpt import head_gpt

        return head_gpt()

    @property
    def typebot(self) -> str:
        """Return the type of bot."""
        return PropertiesCrawJUD.type_bot

    @typebot.setter
    def typebot(self, type_bot: str) -> None:
        """Set the type of bot.

        Args:
            type_bot (str): The new type of bot.

        """
        PropertiesCrawJUD.type_bot = type_bot

    @property
    def state(self) -> str:
        """Return the current state."""
        return PropertiesCrawJUD.state_

    @state.setter
    def state(self, state_: str) -> None:
        """Set the current state.

        Args:
            state_ (str): The new state.

        """
        PropertiesCrawJUD.state_ = state_

    @property
    def path_erro(self) -> Path:
        """Return the error path."""
        return PropertiesCrawJUD.path_erro_

    @path_erro.setter
    def path_erro(self, new_path: Path) -> None:
        """Set the error path.

        Args:
            new_path (Path): The new error path.

        """
        PropertiesCrawJUD.path_erro_ = new_path

    @property
    def name_cert(self) -> str:
        """Return the certificate name."""
        return PropertiesCrawJUD.name_cert_

    @name_cert.setter
    def name_cert(self, name_cert: str) -> None:
        """Set the certificate name.

        Args:
            name_cert (str): The new certificate name.

        """
        PropertiesCrawJUD.name_cert_ = name_cert

    @property
    def client(self) -> str:
        """Return the client information."""
        return PropertiesCrawJUD.client_

    @client.setter
    def client(self, client_: str) -> None:
        """Set the client information.

        Args:
            client_ (str): The new client information.

        """
        PropertiesCrawJUD.client_ = client_

    @property
    def AuthBot(self) -> Callable[[], bool]:  # noqa: N802
        """Return the AuthBot callable."""
        return PropertiesCrawJUD.AuthBot_.auth

    @property
    def MakeXlsx(self) -> _MakeXlsx_:  # noqa: N802
        """Return the MakeXlsx instance."""
        return PropertiesCrawJUD.MakeXlsx_

    @property
    def Interact(self) -> _Interact_:  # noqa: N802
        """Return the Interact instance."""
        return PropertiesCrawJUD.Interact_

    @property
    def SearchBot(self) -> _SearchBot_:  # noqa: N802
        """Return the SearchBot instance."""
        return PropertiesCrawJUD.SearchBot_

    @property
    def OtherUtils(self) -> _OtherUtils_:  # noqa: N802
        """Return the OtherUtils instance."""
        return PropertiesCrawJUD.OtherUtils_

    @property
    def ElementsBot(self) -> ElementsBot_:  # noqa: N802
        """Return the ElementsBot instance."""
        return PropertiesCrawJUD.ElementsBot_

    @property
    def elements(self) -> Union[ESAJ_AM, ELAW_AME, PJE_AM, PROJUDI_AM]:
        """Return the elements configuration."""
        return PropertiesCrawJUD.ElementsBotConfig_

    @elements.setter
    def elements(self, obj: Union[ESAJ_AM, ELAW_AME, PJE_AM, PROJUDI_AM]) -> None:
        PropertiesCrawJUD.ElementsBotConfig_ = obj

    @property
    def driver_launch(self) -> Callable[..., tuple[WebDriver, WebDriverWait]]:  # noqa: N802
        """Return the driver_launch callable."""
        return PropertiesCrawJUD.DriverBot_.driver_launch

    @property
    def search_bot(self) -> Callable[[], bool]:
        """Return the search_bot callable."""
        return self.SearchBot.search_

    @property
    def dataFrame(self) -> Callable[[], list[dict[str, str]]]:  # noqa: N802
        """Return the dataFrame callable."""
        return self.OtherUtils.dataFrame

    @property
    def isStoped(self) -> bool:  # noqa: N802
        """Check if the process is stopped."""
        stopped = Path(self.output_dir_path).joinpath(f"{self.pid}.flag").exists()
        return stopped

    @property
    def elawFormats(self) -> Callable[..., dict[str, str]]:  # noqa: N802
        """Return the elawFormats callable."""
        return self.OtherUtils.elawFormats

    @property
    def calc_time(self) -> Callable[[], list]:
        """Return the calc_time callable."""
        return self.OtherUtils.calc_time

    @property
    def append_moves(self) -> Callable[[], None]:
        """Return the append_moves callable."""
        return self.OtherUtils().append_moves

    @property
    def append_success(self) -> Callable[..., None]:
        """Return the append_success callable."""
        return self.OtherUtils.append_success

    @property
    def append_error(self) -> Callable[..., None]:
        """Return the append_error callable."""
        return self.OtherUtils.append_error

    @property
    def append_validarcampos(self) -> Callable[..., None]:
        """Return the append_validarcampos callable."""
        return self.OtherUtils.append_validarcampos

    @property
    def count_doc(self) -> Callable[..., str | None]:
        """Return the count_doc callable."""
        return self.OtherUtils.count_doc

    @property
    def get_recent(self) -> Callable[..., str | None]:
        """Return the get_recent callable."""
        return self.OtherUtils.get_recent

    @property
    def format_string(self) -> Callable[..., str]:
        """Return the format_string callable."""
        return self.OtherUtils.format_string

    @property
    def normalizar_nome(self) -> Callable[..., str]:
        """Return the normalizar_nome callable."""
        return self.OtherUtils.normalizar_nome

    @property
    def similaridade(self) -> Callable[..., float]:
        """Return the similaridade callable."""
        return self.OtherUtils.similaridade

    @property
    def finalize_execution(self) -> Callable[[], None]:
        """Return the finalize_execution callable."""
        return self.OtherUtils.finalize_execution

    @property
    def install_cert(self) -> Callable[[], None]:
        """Return the install_cert callable."""
        return self.OtherUtils.install_cert

    @property
    def group_date_all(self) -> Callable[..., list[dict[str, str]]]:
        """Return the group_date_all callable."""
        return self.OtherUtils.group_date_all

    @property
    def group_keys(self) -> Callable[..., dict[str, str]]:
        """Return the group_keys callable."""
        return self.OtherUtils.group_keys

    @property
    def gpt_chat(self) -> Callable[..., str]:
        """Analyze a given legal document text and adjust the response based on the document type.

        Uses the OpenAI GPT model to analyze the provided text and generate a response that
        identifies the type of legal document and extracts relevant information based on the
        document type.

        Returns:
            Callable[..., str]: The GPT chat function.

        """
        return self.OtherUtils.gpt_chat

    @property
    def text_is_a_date(self) -> Callable[..., bool]:
        """Return the text_is_a_date callable."""
        return self.OtherUtils.text_is_a_date

    @property
    def name_colunas(self) -> list[str]:
        """Return the name of the columns."""
        return PropertiesCrawJUD.name_colunas_

    @name_colunas.setter
    def name_colunas(self, new_var: list[str]) -> None:
        PropertiesCrawJUD.name_colunas_ = new_var


# from pydantic import BaseModel, ValidationError
# from typing import get_type_hints
# class property(property):
#     def __set__(self, obj, value) -> None:
#         if self.fset is None:
#             raise AttributeError("can't set attribute")

#         try:
#             self.type_ = get_type_hints(self.fget).get("return")
#             self.validate_type(value)
#         except ValidationError as e:
#             raise TypeError(f"Invalid value: {e}")

#         self.fget(obj)
#         self.fset(obj, value)

#     def validate_type(self, value) -> None:
#         """Validate the type of the given value.

#         This method uses a dynamically created Pydantic model to validate
#         that the provided value matches the expected type defined by
#         `self.type_`.

#         Args:
#             value: The value to be validated.
#         Raises:
#             pydantic.ValidationError: If the value does not match the expected type.
#         """

#         class TypedPropertyModel(BaseModel):
#             value: self.type_

#             class Config:
#                 arbitrary_types_allowed = True

#         TypedPropertyModel(value=value)
