"""Queues para execução dos bots."""

from __types import AnyType


class BotQueues:
    """Queues para execução dos bots."""

    def __init__(self, *args: AnyType, **kwargs: AnyType) -> None:
        """Instancia da queue de salvamento de erros."""
        from resources.queues.file_operation import SaveError, SaveSuccess
        from resources.queues.print_message import PrintMessage

        self.print_message = PrintMessage()
        self.append_succes = SaveSuccess()
        self.append_error = SaveError()

    def __call__(self, **kwargs: AnyType) -> None: ...
