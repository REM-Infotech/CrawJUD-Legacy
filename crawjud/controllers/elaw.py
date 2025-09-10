"""Módulo para a classe de controle dos robôs Elaw."""

from __future__ import annotations

import platform
from contextlib import suppress
from pathlib import Path
from time import perf_counter, sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import raise_start_error
from crawjud.controllers.main import CrawJUD
from crawjud.interfaces.types.bots import DataSucesso
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.custom.task import ContextTask
    from crawjud.utils.webdriver.web_element import WebElementBot

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class ElawBot[T](CrawJUD):
    """Classe de controle para robôs do Elaw."""

    def __init__(
        self,
        current_task: ContextTask = None,
        storage_folder_name: str | None = None,
        name: str | None = None,
        system: str | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        """Instancia a classe."""
        self.botname = name
        self.botsystem = system

        self.folder_storage = storage_folder_name
        self.current_task = current_task
        self.start_time = perf_counter()
        self.pid = str(current_task.request.id)

        selected_browser = "chrome"
        if platform.system() == "Linux":
            selected_browser = "firefox"

        super().__init__(selected_browser=selected_browser, *args, **kwargs)

        for k, v in kwargs.copy().items():
            setattr(self, k, v)

        self.download_files()

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

            raise_start_error("Falha na autenticação.")

        self.print_msg(message="Sucesso na autenticação!", type_log="info")
        self._frame = self.load_data()

        sleep(0.5)
        self.print_msg(message="Execução inicializada!", type_log="info")

    def auth(self) -> bool:
        self.driver.get("https://amazonas.elaw.com.br/login")

        # wait until page load
        username = self.wait.until(
            ec.presence_of_element_located((By.ID, "username")),
        )
        username.send_keys(self.username)

        password = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "#password")),
        )
        password.send_keys(self.password)

        entrar = self.wait.until(
            ec.presence_of_element_located((By.ID, "j_id_a_1_5_f")),
        )
        entrar.click()

        sleep(7)

        url = self.driver.current_url

        return url != "https://amazonas.elaw.com.br/login"

    def search(self, bot_data: dict[str, str]) -> bool:
        """Perform an ELAW system search for a legal process.

        Returns:
            bool: True if the process is found; False otherwise.

        Navigates to the appropriate ELAW page, interacts with elements, and clicks to open the process.

        """

        def open_proc() -> bool:
            open_proc = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.ID,
                    "dtProcessoResults:0:btnProcesso",
                )),
            )
            if type_bot.upper() != "CADASTRO":
                if type_bot.upper() == "COMPLEMENT":
                    open_proc = driver.find_element(
                        By.ID,
                        "dtProcessoResults:0:btnEditar",
                    )

                open_proc.click()

            return True

        driver = self.driver
        type_bot = self.type_bot
        interact = self.interact
        wait = self.wait
        bot_data = self.bot_data

        driver.implicitly_wait(5)

        if driver.current_url != el.LINK_PROCESSO_LIST:
            driver.get(el.LINK_PROCESSO_LIST)

        campo_numproc: WebElementBot = wait.until(
            ec.presence_of_element_located((By.ID, "tabSearchTab:txtSearch")),
        )
        campo_numproc.clear()
        sleep(0.15)
        interact.send_key(campo_numproc, bot_data.get("NUMERO_PROCESSO"))
        driver.find_element(By.ID, "btnPesquisar").click()

        try:
            return open_proc()

        except TimeoutException:
            return False

        except StaleElementReferenceException:
            sleep(5)
            return open_proc()

    def elaw_formats(
        self,
        data: dict[str, str],
        cities_amazonas: dict[str, str],
    ) -> dict[str, str]:
        """Formata um dicionário de processo jurídico conforme regras pré-definidas.

        Args:
            data (dict[str, str]): Dicionário de dados brutos.
            cities_amazonas (dict[str, str]): Dicionário das cidades do Amazonas.

        Returns:
            (dict[str, str]): Dados formatados com tipos e valores adequados.

        Examples:
            - Remove chaves com valores vazios ou None.
            - Atualiza "TIPO_PARTE_CONTRARIA" se "TIPO_EMPRESA" for "RÉU".
            - Atualiza "CAPITAL_INTERIOR" conforme "COMARCA".
            - Define "DATA_INICIO" se ausente e "DATA_LIMITE" presente.
            - Formata valores numéricos para duas casas decimais.
            - Define "CNPJ_FAVORECIDO" padrão se vazio.

        """
        # Remove chaves com valores vazios ou None
        self._remove_empty_keys(data)

        # Atualiza "TIPO_PARTE_CONTRARIA" se necessário
        self._update_tipo_parte_contraria(data)

        # Atualiza "CAPITAL_INTERIOR" conforme "COMARCA"
        self._update_capital_interior(data, cities_amazonas)

        # Define "DATA_INICIO" se ausente e "DATA_LIMITE" presente
        self._set_data_inicio(data)

        # Formata valores numéricos
        self._format_numeric_values(data)

        # Define "CNPJ_FAVORECIDO" padrão se vazio
        self._set_default_cnpj(data)

        return data

    def _remove_empty_keys(self, data: dict[str, str]) -> None:
        """Remove chaves com valores vazios ou None."""
        dict_data = data.copy()
        for key in dict_data:
            value = dict_data[key]
            if (isinstance(value, str) and not value.strip()) or value is None:
                data.pop(key)

    def _update_tipo_parte_contraria(self, data: dict[str, str]) -> None:
        """Atualiza 'TIPO_PARTE_CONTRARIA' se 'TIPO_EMPRESA' for 'RÉU'."""
        tipo_empresa = data.get("TIPO_EMPRESA", "").upper()
        if tipo_empresa == "RÉU":
            data["TIPO_PARTE_CONTRARIA"] = "Autor"

    def _update_capital_interior(
        self,
        data: dict[str, str],
        cities_amazonas: dict[str, str],
    ) -> None:
        """Atualiza 'CAPITAL_INTERIOR' conforme 'COMARCA'."""
        comarca = data.get("COMARCA")
        if comarca:
            set_locale = cities_amazonas.get(comarca, "Outro Estado")
            data["CAPITAL_INTERIOR"] = set_locale

    def _set_data_inicio(self, data: dict[str, str]) -> None:
        """Define 'DATA_INICIO' se ausente e 'DATA_LIMITE' presente."""
        if "DATA_LIMITE" in data and not data.get("DATA_INICIO"):
            data["DATA_INICIO"] = data["DATA_LIMITE"]

    def _format_numeric_values(self, data: dict[str, str]) -> None:
        """Formata valores numéricos para duas casas decimais."""
        loop_data = data.items()
        for key, value in loop_data:
            if isinstance(value, (int, float)):
                data[key] = f"{value:.2f}".replace(".", ",")

    def _set_default_cnpj(self, data: dict[str, str]) -> None:
        """Define 'CNPJ_FAVORECIDO' padrão se vazio."""
        if not data.get("CNPJ_FAVORECIDO"):
            data["CNPJ_FAVORECIDO"] = "04.812.509/0001-90"

    def sleep_load(self, element: str) -> None:
        """Wait until the loading indicator for a specific element is hidden."""
        while True:
            sleep(0.5)
            load = None
            aria_value = None
            with suppress(TimeoutException):
                load = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, element)),
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

            div0progress_bar = super().find_element(By.CSS_SELECTOR, div0)
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

    def print_comprovante(self, message: str) -> None:
        numero_processo = self.bot_data.get("NUMERO_PROCESSO")
        name_comprovante = f"Comprovante - {numero_processo} - {self.pid}.png"
        savecomprovante = self.output_dir_path.joinpath(name_comprovante)

        with savecomprovante.open("wb") as fp:
            fp.write(self.driver.get_screenshot_as_png())

        data = DataSucesso(
            NUMERO_PROCESSO=numero_processo,
            MENSAGEM=message,
            NOME_COMPROVANTE=name_comprovante,
            NOME_COMPROVANTE_2="",
        )
        self.append_success(data=data)

        self.print_msg(message=message, type_log="success", row=self.row)
