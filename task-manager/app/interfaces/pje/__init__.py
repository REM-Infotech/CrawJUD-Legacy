from typing import TypedDict

from app.interfaces.pje.payload import ProcessoJudicialDict

from .assuntos import AssuntoDict, ItemAssuntoDict
from .audiencias import AudienciaDict, TipoAudienciaDict
from .partes import (
    PaisDict,
    ParteDict,
    PartesJsonDict,
    PessoaFisicaDict,
    PessoaJuridicaDict,
)
from .worksheet import (
    Assuntos,
    AudienciasProcessos,
    CapaPJe,
    Partes,
    Representantes,
)


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
    "Assuntos",
    "AudienciaDict",
    "AudienciasProcessos",
    "CapaPJe",
    "ItemAssuntoDict",
    "PaisDict",
    "ParteDict",
    "Partes",
    "PartesJsonDict",
    "PessoaFisicaDict",
    "PessoaJuridicaDict",
    "ProcessoJudicialDict",
    "Representantes",
    "TipoAudienciaDict",
]
