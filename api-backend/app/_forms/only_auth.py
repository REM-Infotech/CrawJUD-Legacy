from dataclasses import dataclass

from .head import FormBot


@dataclass
class OnlyAuth(FormBot):
    bot_id: str
    credencial_id: str
