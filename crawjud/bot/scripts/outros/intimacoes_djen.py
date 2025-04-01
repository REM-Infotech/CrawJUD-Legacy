"""Script para captura de intimações do DJEN."""

from time import time
from typing import Self

from selenium.webdriver.common.by import By

from crawjud.bot.core import CrawJUD


class IntimaDJEN(CrawJUD):
    """Classe para captura de intimações do DJEN."""

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """
        Initialize bot instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Andamentos instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def get_intimacoes(self) -> None:
        """Captura as intimações do DJEN."""
        rows_intimacoes = self.driver.find_element(By.CSS_SELECTOR, 'div[class="mat-tab-body-wrapper"]')
        rows_intimacoes = rows_intimacoes.find_elements(By.CSS_SELECTOR, 'div[class="ng-star-inserted"]')

        for _ in rows_intimacoes:
            # for loop
            ...
