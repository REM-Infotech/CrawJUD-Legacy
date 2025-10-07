"""Defina tipos de dicionário para credenciais de sistemas judiciais diversos.

Este módulo fornece:
- CredendialDictSelect: estrutura para seleção de credenciais;
- CredendialsSystemDict: estrutura para listas de credenciais por sistema;
- CredendialsDict: estrutura para credenciais individuais.

"""

from __future__ import annotations

from typing import TypedDict


class CredendialDictSelect(TypedDict):
    """Defina o dicionário de seleção de credenciais para sistemas judiciais diversos.

    Args:
        value (int | None): Valor identificador da credencial ou None.
        text (str): Texto descritivo da credencial.
        disabled (bool): Indica se a credencial está desabilitada.

    Returns:
        TypedDict: Estrutura de dados para seleção de credenciais.

    """

    value: int | None
    text: str
    disabled: bool


class CredendialsSystemDict(TypedDict):
    """Defina o dicionário de listas de credenciais para cada sistema judicial.

    Args:
        elaw (list[CredendialDictSelect]): Lista de credenciais para o sistema eLaw.
        projudi (list[CredendialDictSelect]): Lista de credenciais para o sistema Projudi.
        esaj (list[CredendialDictSelect]): Lista de credenciais para o sistema ESAJ.
        pje (list[CredendialDictSelect]): Lista de credenciais para o sistema PJe.

    Returns:
        TypedDict: Estrutura de dados contendo listas de credenciais por sistema.

    """

    elaw: list[CredendialDictSelect]
    projudi: list[CredendialDictSelect]
    esaj: list[CredendialDictSelect]
    pje: list[CredendialDictSelect]


class CredendialsDict(TypedDict):
    """Defina o dicionário de credenciais individuais para sistemas judiciais.

    Args:
        id (int): Identificador único da credencial.
        nome_credencial (str): Nome descritivo da credencial.
        system (str): Nome do sistema judicial associado.
        login_method (str): Método de autenticação utilizado.

    Returns:
        TypedDict: Estrutura de dados representando uma credencial individual.

    """

    id: int
    nome_credencial: str
    system: str
    login_method: str
