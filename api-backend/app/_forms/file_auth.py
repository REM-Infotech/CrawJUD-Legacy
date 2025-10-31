from dataclasses import dataclass

from .head import FormBot


@dataclass
class FileAuth(FormBot):
    bot_id: str
    sid_filesocket: str
    credencial: str
    planilha_xlsx: str
