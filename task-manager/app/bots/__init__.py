"""Defina funcionalidades dos bots do sistema.

Este pacote reúne módulos responsáveis por diferentes
operações automatizadas, como administração, busca,
cálculo, capa, emissão, intimações, movimentação e protocolo.
"""

import _hook as hook

from . import (
    admin,
    buscadores,
    calculadoras,
    capa,
    emissao,
    intimacoes,
    movimentacao,
    protocolo,
)

__all__ = [
    "admin",
    "buscadores",
    "calculadoras",
    "capa",
    "emissao",
    "hook",
    "intimacoes",
    "movimentacao",
    "protocolo",
]
