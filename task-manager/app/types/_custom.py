import re
from collections import UserString
from contextlib import suppress
from re import Pattern
from typing import NoReturn

from app.types import AnyType
from common.exceptions.validacao import ValidacaoStringError
from constants import PADRAO_CNJ


class StrProcessoCNJ(UserString):
    """Classe(str) StrProcessoCNJ para processos no padrão CNJ.

    Esta classe permite criar e verificar se o valor corresponde ao

    Args:
        instance (Any): Instância a ser verificada.

    Returns:
        bool: Indica se a instância corresponde a algum dos padrões de data/hora.

    """

    def __raise_value_error__(self) -> NoReturn:
        raise ValidacaoStringError(
            message="Valor informado não corresponde ao valor esperado",
        )

    def __validate_str__(
        self,
        seq: str,
        pattern_list: list[Pattern],
    ) -> bool:
        validate_seq = any(re.match(pattern, seq) for pattern in pattern_list)

        if not validate_seq:
            self.__raise_value_error__()

    def __init__(self, seq: str) -> None:
        """Inicializa a classe StrTime."""
        self.__validate_str__(seq, PADRAO_CNJ)

        seq = re.sub(
            r"(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})",
            r"\1-\2.\3.\4.\5.\6",
            seq,
        )

        super().__init__(seq)

    @property
    def tj(self) -> str:
        """Extrai o ID do TJ.

        Returns:
            str: TJ ID

        """
        to_return = None
        match_ = re.search(r"\.(\d)\.(\d{1,2})\.", self.data)
        if not match_:
            self.__raise_value_error__()

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

    def __repr__(self) -> str:
        """Retorne a representação formal da instância StrTime.

        Returns:
            str: Representação formal da instância.

        """
        return self

    def __instancecheck__(self, instance: AnyType) -> bool:
        """Verifique se a instância corresponde a padrões de string CNJ.

        Args:
            instance: Instância a ser verificada.

        Returns:
            bool: Indica se a instância corresponde a algum dos padrões de string CNJ.

        """
        with suppress(ValueError):
            return self.__validate_str__(instance, PADRAO_CNJ)

        return False
