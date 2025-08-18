"""Initialize and run the ESaj bot for CrawJUD-Bots.

This module configures and initializes the ESaj bot components including BuscaPags,
Capa, Emissao, Movimentacao, and Protocolo. It sets logging and error handling.
"""

from crawjud.bots.esaj.busca_pags import BuscaPags as Busca_pags
from crawjud.bots.esaj.capa import Capa
from crawjud.bots.esaj.emissao import Emissao
from crawjud.bots.esaj.movimentacao import Movimentacao
from crawjud.bots.esaj.protocolo import Protocolo
from crawjud.common.exceptions.bot import StartError

__all__ = ["Busca_pags", "Capa", "Emissao", "Movimentacao", "Protocolo", "StartError"]
