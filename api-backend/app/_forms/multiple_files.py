from dataclasses import dataclass

from .head import FormBot


@dataclass
class MultipleFiles(FormBot):
    bot_id: str
    credencial_id: str

    xlsx: str
    xlsx_sid: str

    outros_arquivos: list[str]
    outros_arquivos_sid: str
