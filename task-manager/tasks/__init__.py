"""Task module for Celery."""

import bots as _bots
from __types import MessageType
from celery import shared_task

__all__ = ["_bots"]


@shared_task(name="print_msg")
def print_msg(message: str, msg_type: MessageType = "info") -> None:
    """Print mensagem."""
