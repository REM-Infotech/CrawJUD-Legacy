"""Queues para execução dos bots."""

from __types import AnyType


class BotQueues:
    """Queues para execução dos bots."""

    def __init__(self, **kwargs: AnyType) -> None:
        """Instancia da queue de salvamento de erros."""

    def __call__(self, **kwargs: AnyType) -> None: ...
