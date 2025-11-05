"""Operações de planilhas."""

from typing import TYPE_CHECKING

from app.types import AnyType

DATASAVE = []

if TYPE_CHECKING:
    from bots.head import CrawJUD


class SaveSuccess:
    """Controle da Queue de salvamento de sucessos."""

    bot: CrawJUD

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot

    def __call__(self, *args: AnyType, **kwargs: AnyType) -> None: ...


class SaveError:
    """Controle da Queue de salvamento de erros."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de erros."""
        self.bot = bot

    def __call__(self, *args: AnyType, **kwargs: AnyType) -> None: ...
