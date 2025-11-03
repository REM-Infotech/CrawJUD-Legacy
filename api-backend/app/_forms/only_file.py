from dataclasses import dataclass

from .head import FormBot


@dataclass
class OnlyFile(FormBot):
    bot_id: str
    sid_filesocket: str
    planilha_xlsx: str


@dataclass
class Pje(FormBot):
    __name__ = "pje"

    bot_id: str
    sid_filesocket: str
    planilha_xlsx: str
