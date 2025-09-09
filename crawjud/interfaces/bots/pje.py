"""Modulo de tipos utilizados para representar estrutura de dados do PJe.

Inclui definições de TypedDict para endereços, papéis, representantes, polos,
assuntos, anexos, itens de processo, expedientes e processos, facilitando a
tipagem e documentação dos dados manipulados pelos bots.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from crawjud.interfaces.systems.pje.processos import ProcessoJudicialDict as Processo

if TYPE_CHECKING:
    from crawjud.interfaces.bots.data import BotData
    from crawjud.interfaces.systems.pje.processos import ProcessoJudicialDict
    from crawjud.interfaces.core.primitives import DictType


class DictSeparaRegiao(TypedDict):
    """Define o dicionário que separa regiões e posições de processos.

    Args:
        regioes (dict[str, list[BotData]]): Dicionário de regiões e bots.
        position_process (dict[str, int]): Posição dos processos por região.

    """

    regioes: dict[str, list[BotData]]
    position_process: dict[str, int]


class Resultados(TypedDict):
    """Define o retorno do desafio contendo headers, cookies e resultados.

    Args:
        headers (DictType): Cabeçalhos da requisição.
        cookies (DictType): Cookies da requisição.
        results (DictResults): Resultados do desafio.

    Returns:
        Resultados: Dicionário com informações do retorno do desafio.

    """

    headers: DictType
    cookies: DictType
    results: DictResults


class DictDesafio(TypedDict):
    """Define o desafio do PJe, contendo a imagem codificada e o token do desafio.

    Args:
        imagem (Base64Str): Imagem do desafio em base64.
        tokenDesafio (str): Token associado ao desafio.

    Returns:
        DictDesafio: Dicionário com informações do desafio.

    """

    imagem: str
    tokenDesafio: str


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


__all__ = ["Processo"]
