from __future__ import annotations
from importlib import import_module
from typing import Self, Union

from ...shared import PropertiesCrawJUD


class ElementsBot(PropertiesCrawJUD):

    elements_bot = None

    def __init__(
        self, elements_base: Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]
    ) -> None:
        self.elements_bot = elements_base

    @classmethod
    def init_elements(cls, self: Self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
        return ElementsBot(
            getattr(
                import_module(f".{self.system.lower()}", __package__),
                f"{self.system.upper()}_{self.state_or_client.upper()}",
            )
        ).Elements

    @property
    def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
        return self.elements_bot


if __name__ == "__main__":

    from .elaw import ELAW_AME
    from .esaj import ESAJ_AM
    from .pje import PJE_AM
    from .projudi import PROJUDI_AM

    # @property
    # def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
    #     """Retorna a configuração de acordo com o estado ou cliente."""

    #     return self.objeto


ElementsBot.init_elements("").Elements
