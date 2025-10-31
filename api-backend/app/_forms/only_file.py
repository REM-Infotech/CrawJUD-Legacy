from dataclasses import dataclass

from .head import FormBot


@dataclass
class OnlyFile(FormBot):
    bot_id: str
    xlsx: str
    xlsx_sid: str
