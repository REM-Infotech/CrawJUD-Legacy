from typing import Any, Literal, ParamSpec, TypedDict, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

MyAny = Any

type Methods = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
type ConfigNames = Literal[
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
]
type ModeMiddleware = Literal["legacy", "modern"]


class HealtCheck(TypedDict):
    status: str
    database: str
    timestamp: str


class LoginForm(TypedDict):
    login: str
    password: str
    remember: bool
