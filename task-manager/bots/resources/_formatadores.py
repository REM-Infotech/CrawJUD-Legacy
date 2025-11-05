from unicodedata import combining, normalize

from werkzeug.utils import secure_filename


def formata_string(string: str) -> str:
    normalized_string = "".join([
        c for c in normalize("NFKD", string) if not combining(c)
    ])

    return secure_filename(normalized_string).upper()
