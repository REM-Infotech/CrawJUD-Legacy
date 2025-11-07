from typing import TypedDict

from app.types import MessageType, StatusBot


class Message(TypedDict, total=False):
    pid: str
    message: str
    message_type: MessageType
    status: StatusBot
    start_time: str
    row: int
    total: int
    error_count: int
    success_count: int
    remaining_count: int
