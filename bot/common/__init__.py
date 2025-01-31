"""Common module initialization for CrawJUD-Bots, handling custom exceptions."""

from .exceptions import ErroDeExecucao, ItemNaoEcontrado, StartError

__all__ = ["ErroDeExecucao", "ItemNaoEcontrado", "StartError"]
