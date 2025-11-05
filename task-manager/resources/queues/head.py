"""Queues para execução dos bots."""

from __types import AnyType


class BotQueues:
    """Queues para execução dos bots."""

    def __init__(self, *args: AnyType, **kwargs: AnyType) -> None:
        """Instancia da queue de salvamento de erros."""
