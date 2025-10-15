"""Empty."""

import json
from pathlib import Path

from app.interfaces._cidades_am import CidadesAmazonas

cidades_amazonas: CidadesAmazonas = {}


def _load_cidades_amazonas() -> None:
    home = Path(__file__).cwd().joinpath("crawjud")
    json_cidades_am_ = home.joinpath(
        "common",
        "cidades_amazonas.json",
    )
    with json_cidades_am_.open("r") as fp:
        global cidades_amazonas
        cidades_amazonas = json.loads(fp.read())


_load_cidades_amazonas()

__all__ = ["cidades_amazonas"]
