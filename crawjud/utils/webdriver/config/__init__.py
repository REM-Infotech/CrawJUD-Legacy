"""Pacote público para configuração do webdriver.

Inclui definições e utilitários para configuração do webdriver.
"""

from __future__ import annotations

from crawjud.utils.webdriver.config.chrome import configure_chrome
from crawjud.utils.webdriver.config.firefox import configure_gecko

__all__ = ["configure_chrome", "configure_gecko"]
