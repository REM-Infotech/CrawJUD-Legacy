"""Módulo para a classe de controle dos robôs Elaw."""

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app.controllers.head import CrawJUD
from app.resources.auth import AutenticadorElaw
from app.resources.search import ElawSearch
from constants.data._bots.cidades import cidades_amazonas

if TYPE_CHECKING:
    from pathlib import Path


class ElawBot(CrawJUD):
    """Classe de controle para robôs do Elaw."""

    def __init__(self) -> None:
        """Inicialize o robô Elaw."""
        self.search = ElawSearch(self)
        self.auth = AutenticadorElaw(self)

    def elaw_formats(
        self,
        data: dict[str, str],
    ) -> dict[str, str]:
        # Remove chaves com valores vazios ou None
        self._remove_empty_keys(data)

        # Atualiza "TIPO_PARTE_CONTRARIA" se necessário
        self._update_tipo_parte_contraria(data)

        # Atualiza "CAPITAL_INTERIOR" conforme "COMARCA"
        self._update_capital_interior(data, cidades_amazonas)

        # Define "DATA_INICIO" se ausente e "DATA_LIMITE" presente
        self._set_data_inicio(data)

        # Formata valores numéricos
        self._format_numeric_values(data)

        # Define "CNPJ_FAVORECIDO" padrão se vazio
        self._set_default_cnpj(data)

        return data

    def sleep_load(self, element: str) -> None:
        """Wait until the loading indicator for a specific element is hidden."""
        while True:
            sleep(0.5)
            load = None
            aria_value = None
            with suppress(TimeoutException):
                load = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        element,
                    )),
                )

            if load:
                for attributes in ["aria-live", "aria-hidden", "class"]:
                    aria_value = load.get_attribute(attributes)

                    if not aria_value:
                        continue

                    break

                if aria_value is None or any(
                    value == aria_value
                    for value in [
                        "off",
                        "true",
                        "spinner--fullpage spinner--fullpage--show",
                    ]
                ):
                    break

            if not load:
                break

    def wait_fileupload(self) -> None:
        while True:
            sleep(0.05)
            div1 = 'div[class="ui-fileupload-files"]'
            div2 = 'div[class="ui-fileupload-row"]'
            div0 = 'div[id*=":uploadGedEFile"]'
            progress_bar = None

            div0progress_bar = super().find_element(
                By.CSS_SELECTOR,
                div0,
            )
            div1progress_bar = div0progress_bar.find_element(
                By.CSS_SELECTOR,
                div1,
            )

            with suppress(NoSuchElementException):
                progress_bar = div1progress_bar.find_element(
                    By.CSS_SELECTOR,
                    div2,
                )

            if progress_bar is None:
                break

    def screenshot_iframe(
        self,
        url_page: str,
        path_comprovante: Path,
    ) -> None:
        driver = self.driver
        main_window = driver.current_window_handle

        self.driver.switch_to.new_window("tab")
        self.driver.get(url_page)

        sleep(5)

        bytes_png = self.driver.get_screenshot_as_png()

        with path_comprovante.open("wb") as fp:
            fp.write(bytes_png)

        self.driver.close()

        self.driver.switch_to.window(main_window)
