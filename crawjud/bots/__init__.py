"""Módulo de Bots - Robôs de Automação Judicial.

Este módulo contém os robôs de automação para diversos sistemas judiciais 
brasileiros. Cada bot é especializado em um sistema específico e implementa 
funcionalidades como consulta de processos, protocolos e operações automatizadas.

Sistemas suportados:
    - PJe: Processo Judicial Eletrônico (Tribunais Federais)
    - ESAJ: Sistema de Automação da Justiça (TJSP)
    - Projudi: Processo Judicial Digital (TJs Estaduais)
    - E-law: Sistema de gestão processual
    - JusBr: Portal de consultas jurídicas
    - CSI: Central de Sistemas Integrados
    - Caixa: Sistemas da Caixa Econômica Federal

Arquitetura dos bots:
    - Interface comum para todos os bots
    - Gerenciamento automático de WebDriver
    - Sistema de autenticação unificado
    - Tratamento robusto de erros
    - Logging estruturado

Exemplo de uso:
    >>> from crawjud.bots.pje import PJeBot
    >>> 
    >>> bot = PJeBot(credentials, config)
    >>> await bot.initialize()
    >>> resultado = await bot.consultar_processo("1234567-89.2023.4.01.3456")

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

from __future__ import annotations

from . import csi, elaw, esaj, jusbr, pje, projudi

__all__ = ["csi", "elaw", "esaj", "jusbr", "pje", "projudi"]
