"""Package: scripts.

This package contains various scripts for different systems within the CrawJUD-Bots application, including projudi, esaj, elaw, pje, calculadoras, and caixa.
"""

from typing import Union

from .caixa import caixa
from .calculadoras import calculadoras
from .elaw import elaw
from .esaj import esaj
from .pje import pje
from .projudi import projudi

__all__ = [projudi, esaj, elaw, pje, calculadoras, caixa]

ClassesSystems = Union[caixa, elaw, esaj, projudi, pje, caixa, calculadoras]
