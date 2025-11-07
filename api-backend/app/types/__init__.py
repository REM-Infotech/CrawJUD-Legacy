from datetime import datetime, timedelta
from typing import Any, Literal, ParamSpec, TypedDict, TypeVar

MyAny = Any

P = ParamSpec("P", bound=MyAny)
T = TypeVar("T", bound=MyAny)


type Sistemas = Literal[
    "projudi",
    "elaw",
    "esaj",
    "pje",
    "jusds",
    "csi",
]
type MessageType = Literal["info", "log", "error", "warning", "success"]
type Methods = Literal[
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "OPTIONS",
]
type ConfigNames = Literal[
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
]
type ModeMiddleware = Literal["legacy", "modern"]


type ListPartes = list[
    tuple[list[dict[str, str]], list[dict[str, str]]]
]
type MethodsSearch = Literal["peticionamento", "consulta"]
type PolosProcessuais = Literal["Passivo", "Ativo"]
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes
type Dict = dict[str, PyStrings | PyNumbers]
type ListDict = list[Dict]
type StatusBot = Literal["Inicializando", "Em Execução", "Finalizado"]


class HealtCheck(TypedDict):
    status: str
    database: str
    timestamp: str


class LoginForm(TypedDict):
    login: str
    password: str
    remember: bool
