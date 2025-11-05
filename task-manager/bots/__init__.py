"""Módulo de Bots - Robôs de Automação Judicial.

Este módulo contém os robôs de automação para diversos sistemas judiciais
brasileiros. Cada bot é especializado em um sistema específico e implementa
funcionalidades como consulta de processos, protocolos e operações automatizadas.

Módulos disponíveis:
    - pje: Robôs para sistema PJe
    - esaj: Robôs para sistema ESAJ
    - projudi: Robôs para sistema Projudi
    - elaw: Robôs para sistema E-law
    - jusbr: Robôs para JusBr
    - csi: Robôs para CSI
    - caixa: Robôs para sistemas da Caixa
    - calculadoras: Bots para cálculos automáticos
"""

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
    "intimacoes",
    "movimentacao",
    "protocolo",
]
