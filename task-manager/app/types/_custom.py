import re
from collections import UserString
from contextlib import suppress
from typing import TYPE_CHECKING

from common._raises import value_error
from constants import PADRAO_CNJ

if TYPE_CHECKING:
    from app.types import AnyType


class StrProcessoCNJ(UserString):
    """Classe(str) StrProcessoCNJ para processos no padrão CNJ.

    Esta classe permite criar e verificar se o valor corresponde ao

    Args:
        instance (Any): Instância a ser verificada.

    Returns:
        bool: Indica se a instância corresponde a algum dos padrões de data/hora.

    """

    def __init__(self, seq: str) -> None:
        """Inicializa a classe StrTime."""
        super().__init__(seq)
        self.__validate_str()

        seq = re.sub(
            r"(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})",
            r"\1-\2.\3.\4.\5.\6",
            seq,
        )

    def __validate_str(self) -> bool:
        matches = [re.match(pattern, self.data) for pattern in PADRAO_CNJ]

        return any(matches) or value_error()

    @property
    def tj(self) -> str:
        """Extrai o ID do TJ.

        Returns:
            str: TJ ID

        """
        to_return = None
        match_ = re.search(r"\.(\d)\.(\d{1,2})\.", self.data)
        if not match_:
            value_error()

        to_return: str = match_.group(2)
        if to_return.startswith("0"):
            to_return = to_return.replace("0", "")

        return to_return

    def __str__(self) -> str:
        """Retorne a representação em string da instância StrTime.

        Returns:
            str: Representação textual da instância.

        """
        return self.data

    def __instancecheck__(self, instance: AnyType) -> bool:
        """Verifique se a instância corresponde a padrões de string CNJ.

        Args:
            instance: Instância a ser verificada.

        Returns:
            bool: Indica se a instância corresponde a algum dos padrões de string CNJ.

        """
        with suppress(ValueError):
            matches = [re.match(pattern, instance) for pattern in PADRAO_CNJ]
            return any(matches) or value_error()

        return False
