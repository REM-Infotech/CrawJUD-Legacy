"""Defina tipos para assuntos e itens de assunto do JSON do PJe.

Fornece os dicionários tipados AssuntoDict e ItemAssuntoDict para estruturar e
validar os dados de assuntos e itens de assunto conforme o padrão do sistema PJe.

"""

from __future__ import annotations

from typing import TypedDict


class AssuntoDict(TypedDict):
    """Defina o dicionário tipado para o campo 'assunto' do JSON de assuntos.

    Args:
            id (int): Identificador do assunto
            idAssuntoSuperior (int): Identificador do assunto superior
            codigo (str): Código do assunto
            descricao (str): Descrição do assunto
            assuntoCompleto (str): Caminho completo do assunto
            assuntoResumido (str): Caminho resumido do assunto
            nivel (int): Nível hierárquico do assunto
            podeAdicionarAoProcesso (bool): Indica se pode ser adicionado ao processo
            possuiFilhos (bool): Indica se possui assuntos filhos

    Returns:
            dict: Estrutura tipada do assunto

    """

    id: int
    idAssuntoSuperior: int
    codigo: str
    descricao: str
    assuntoCompleto: str
    assuntoResumido: str
    nivel: int
    podeAdicionarAoProcesso: bool
    possuiFilhos: bool


class ItemAssuntoDict(TypedDict):
    """Defina o dicionário tipado para um item de assunto do JSON de assuntos.

    Args:
            id (int): Identificador do item de assunto
            idProcesso (int): Identificador do processo
            assunto (AssuntoDict): Estrutura do assunto
            principal (bool): Indica se é o assunto principal

    Returns:
            dict: Estrutura tipada do item de assunto

    """

    id: int
    idProcesso: int
    assunto: AssuntoDict
    principal: bool
