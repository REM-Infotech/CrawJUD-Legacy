from typing import Any, Literal, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

MyAny = Any

type Methods = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
type ConfigNames = Literal[
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
]
