"""Módulo para a classe de controle dos robôs PJe."""

from typing import TYPE_CHECKING, ClassVar

from dotenv import load_dotenv

from app.controllers.head import CrawJUD
from app.resources import RegioesIterator
from app.resources.auth.pje import AutenticadorPJe
from app.resources.search.pje import PjeSeach

load_dotenv()

if TYPE_CHECKING:
    from app.interfaces import BotData
    from app.types import Dict


class PjeBot(CrawJUD):
    """Classe de controle para robôs do PJe."""

    posicoes_processos: ClassVar[Dict] = {}

    def __init__(self) -> None:
        self.auth = AutenticadorPJe(self)
        self.search = PjeSeach(self)

    @property
    def list_posicao_processo(self) -> dict[str, int]:
        return self.posicoes_processos

    @property
    def data_regiao(self) -> list[BotData]:
        return self._data_regiao

    @data_regiao.setter
    def data_regiao(self, _data_regiao: str) -> None:
        self._data_regiao = _data_regiao

    @property
    def regiao(self) -> str:
        return self._regiao

    @regiao.setter
    def regiao(self, _regiao: str) -> None:
        self._regiao = _regiao

    def regioes(self) -> RegioesIterator:
        """Listagem das regiões do PJe.

        Returns:
            RegioesIterator:
                Iterator das Regiões do PJe.

        """
        return RegioesIterator(self)
