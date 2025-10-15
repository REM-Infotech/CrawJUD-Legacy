"""Initialize and manage the Caixa bot for the CrawJUD-Bots with docstrings up to standard.

Provide a class interface to run the Emissor bot, handle exceptions, and
configure logging. This file follows Google/PEP 257 docstring guidelines.
"""

from __future__ import annotations

from app.bots.caixa.emissor import Emissor

__all__ = ["Emissor"]
