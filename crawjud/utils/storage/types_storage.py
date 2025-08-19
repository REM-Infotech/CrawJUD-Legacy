"""Defina tipos literais para identificar backends de armazenamento suportados.

Este módulo define tipos literais para os backends de armazenamento aceitos
no sistema, facilitando a validação e a tipagem dos parâmetros relacionados.

"""

from __future__ import annotations

from typing import Literal

storages = Literal["google", "minio"]
