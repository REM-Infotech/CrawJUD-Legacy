from typing import Literal, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

type Methods = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
type ConfigNames = Literal[
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
]
