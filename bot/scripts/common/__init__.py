"""
Module: common.

This module aggregates and exposes common exception classes used throughout the CrawJUD-Bots application.
"""

from .exceptions import ErroDeExecucao, ItemNaoEcontrado, StartError

__all__ = ["ErroDeExecucao", "ItemNaoEcontrado", "StartError"]
