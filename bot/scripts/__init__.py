"""Package: scripts.

This package contains various scripts for different systems within the CrawJUD-Bots application, including Projudi, Esaj, Elaw, PJe, calculadoras, and caixa.
"""  # noqa: E501

from typing import Union

from .caixa import Caixa
from .calculadoras import Calculadoras
from .elaw import Elaw
from .esaj import Esaj
from .pje import PJe
from .projudi import Projudi

__all__ = [Projudi, Esaj, Elaw, PJe, Calculadoras, Caixa]

ClassesSystems = Union[Caixa, Elaw, Esaj, Projudi, PJe, Calculadoras]
