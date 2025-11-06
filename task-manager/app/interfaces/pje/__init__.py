from typing import TYPE_CHECKING, TypedDict

from .assuntos import AssuntoDict, ItemAssuntoDict
from .audiencias import AudienciaDict, TipoAudienciaDict
from .partes import (
    PaisDict,
    ParteDict,
    PartesJsonDict,
    PessoaFisicaDict,
    PessoaJuridicaDict,
)

if TYPE_CHECKING:
    from app.interfaces.pje.payload import ProcessoJudicialDict


class DictResults(TypedDict):
    """Define os resultados retornados pelo desafio do PJe.

    Args:
        id_processo (str): Identificador do processo.
        captchatoken (str): Token do captcha.
        text (str): Texto de resposta.
        data_request (Processo): Dados do processo retornados.

    Returns:
        DictResults: Dicionário com informações dos resultados do desafio.

    """

    id_processo: str
    data_request: ProcessoJudicialDict


__all__ = [
    "AssuntoDict",
    "AudienciaDict",
    "ItemAssuntoDict",
    "PaisDict",
    "ParteDict",
    "PartesJsonDict",
    "PessoaFisicaDict",
    "PessoaJuridicaDict",
    "TipoAudienciaDict",
]
