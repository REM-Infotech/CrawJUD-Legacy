"""Sistema de envio de logs para o ClientUI."""

from typing import TYPE_CHECKING, TypedDict

from dotenv import load_dotenv

from __types import AnyType, MessageType

from .head import BotQueues

if TYPE_CHECKING:
    from bots.head import CrawJUD

load_dotenv()


class Count(TypedDict):
    """Dicionario de contagem."""

    success_count: int = 0
    remainign_count: int = 0
    error_count: int = 0


class PrintMessage(BotQueues):
    """Envio de logs para o FrontEnd."""

    bot: CrawJUD
    _message_type: MessageType

    def __init__(self, **kwargs: AnyType) -> None:
        """Instancia da queue de salvamento de erros."""

    def __call__(self, **kwargs: AnyType) -> None: ...
