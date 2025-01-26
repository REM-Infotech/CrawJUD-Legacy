from __future__ import annotations

from importlib import import_module
from typing import Self, Union

from ...core import CrawJUD
from .elaw import ELAW_AME
from .esaj import ESAJ_AM
from .pje import PJE_AM
from .projudi import PROJUDI_AM


class ElementsBot(CrawJUD):

    elements_bot = None

    def __init__(
        self,
    ) -> None:
        """"""

    def Config(self) -> Self:

        if self.elements_bot is None:
            self.elements_bot = getattr(
                import_module(f".{self.system.lower()}", __package__),
                f"{self.system.upper()}_{self.state_or_client.upper()}",
            )

        return self

    @property
    def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
        return self.elements_bot

    # @property
    # def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
    #     """Retorna a configuração de acordo com o estado ou cliente."""

    #     return self.objeto
