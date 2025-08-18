"""Module for initializing and orchestrating ELAW system automation bots.

This module serves as the main entry point for ELAW system automation, providing bot
initialization, management and execution capabilities for various ELAW tasks.

Classes:
    Elaw: Core class for managing ELAW automation bots

Attributes:
    logger_ (Logger): Module logger instance
    ClassBots (Union): Union type of available bot classes

"""

from __future__ import annotations

from crawjud.bots.elaw.andamentos import Andamentos
from crawjud.bots.elaw.cadastro import ElawCadadastro
from crawjud.bots.elaw.download import Download
from crawjud.bots.elaw.prazos import Prazos
from crawjud.bots.elaw.provisao import Provisao
from crawjud.bots.elaw.sol_pags import SolPags as Sol_pags

__all__ = [
    "Andamentos",
    "Download",
    "ElawCadadastro",
    "Prazos",
    "Provisao",
    "Sol_pags",
]
