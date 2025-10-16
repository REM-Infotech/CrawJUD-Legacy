import json
from pathlib import Path

_data = json.loads(Path(__file__).with_suffix(".json").read_text())
VARAS = dict[str, str]
# expõe as chaves como variáveis
globals().update(_data)
