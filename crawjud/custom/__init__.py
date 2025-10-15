"""Pacote público para módulos customizados do sistema.

Inclui extensões e customizações específicas do projeto.
"""

from __future__ import annotations

from .celery import AsyncCelery

__all__ = ["AsyncCelery"]
