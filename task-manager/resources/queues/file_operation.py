"""Operações de planilhas."""

from typing import TYPE_CHECKING

from __types import AnyType

from .head import BotQueues

DATASAVE = []

if TYPE_CHECKING:
    from bots.head import CrawJUD


class SaveSuccess(BotQueues):
    """Controle da Queue de salvamento de sucessos."""

    bot: CrawJUD

    def __init__(self, **kwargs: AnyType) -> None:
        """Instancia da queue de salvamento de sucessos."""

    def __call__(self, **kwargs: AnyType) -> None: ...


class SaveError(BotQueues):
    """Controle da Queue de salvamento de erros."""

    def __init__(self, **kwargs: AnyType) -> None:
        """Instancia da queue de salvamento de erros."""

    def __call__(self, **kwargs: AnyType) -> None: ...
