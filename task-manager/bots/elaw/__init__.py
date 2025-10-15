"""Module for initializing and orchestrating ELAW system automation bots.

This module serves as the main entry point for ELAW system automation, providing bot
initialization, management and execution capabilities for various ELAW tasks.

Classes:
    Elaw: Core class for managing ELAW automation bots

Attributes:
    logger_ (Logger): Module logger instance
    ClassBots (Union): Union type of available bot classes

"""

from app.bots.elaw import (
    andamentos,
    cadastro,
    download,
    provisao,
    solicita_pagamento,
)

__all__ = [
    "andamentos",
    "cadastro",
    "download",
    "provisao",
    "solicita_pagamento",
]
