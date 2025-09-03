"""Initialize and run the ESaj bot for CrawJUD-Bots.

This module configures and initializes the ESaj bot components including BuscaPags,
Capa, Emissao, Movimentacao, and Protocolo. It sets logging and error handling.
"""

from crawjud.bots.esaj import (
    busca_pags,
    capa,
    emissao,
    movimentacao,
    protocolo,
)

__all__ = [
    "busca_pags",
    "capa",
    "emissao",
    "movimentacao",
    "protocolo",
]
