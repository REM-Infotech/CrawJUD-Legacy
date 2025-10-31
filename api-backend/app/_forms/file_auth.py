from dataclasses import dataclass

from .head import FormBot


@dataclass
class FileAuth(FormBot):
    bot_id: str
    credencial_id: str
    xlsx: str
    xlsx_sid: str
