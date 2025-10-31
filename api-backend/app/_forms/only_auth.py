from dataclasses import dataclass

from .head import FormBot


@dataclass
class OnlyAuth(FormBot):
    bot_id: str
    sid_filesocket: str
    credencial: str
