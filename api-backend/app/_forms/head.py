from typing import ClassVar, Self

from __types import Dict


class FormBot:
    _subclass: ClassVar[dict[str, type[Self]]] = {}

    @classmethod
    def load_form(cls, form_name: str, kwargs: Dict) -> Self:
        return cls._subclass[form_name](**kwargs)

    def to_dict(self) -> Dict:
        return {
            key.lower(): getattr(self, key, None)
            for key in dir(self)
            if getattr(self, key, None)
            and not key.startswith("_")
            and not callable(getattr(self, key, None))
        }

    def __init_subclass__(cls: type[Self]) -> None:
        cls._subclass[cls.__module__.split(".")[-1]] = cls
