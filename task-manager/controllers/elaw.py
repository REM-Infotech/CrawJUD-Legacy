"""Módulo para a classe de controle dos robôs Elaw."""

from contextlib import suppress
from pathlib import Path
from time import sleep

from resources.elements import elaw as el
from resources.web_element import WebElementBot
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from controllers._master import CrawJUD

cidades_amazonas = {}


class ElawBot(CrawJUD):
    """Classe de controle para robôs do Elaw."""

    def auth(self) -> bool:
        self.driver.get("https://amazonas.elaw.com.br/login")

        # wait until page load
        username = self.wait.until(
            ec.presence_of_element_located((By.ID, "username")),
        )
        username.send_keys(self.username)

        password = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "#authKey")),
        )
        password.send_keys(self.password)

        entrar = self.wait.until(
            ec.presence_of_element_located((By.ID, "j_id_c_1_5_f")),
        )
        entrar.click()

        sleep(7)

        url = self.driver.current_url
        return url != "https://amazonas.elaw.com.br/login"

    def search(self, bot_data: dict[str, str]) -> bool:
        wait = self.wait
        bot_data = self.bot_data

        numero_processo = bot_data.get("NUMERO_PROCESSO")

        message = f"Buscando processo {numero_processo}"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        self.driver.implicitly_wait(5)

        if self.driver.current_url != el.LINK_PROCESSO_LIST:
            self.driver.get(el.LINK_PROCESSO_LIST)

        campo_numproc: WebElementBot = wait.until(
            ec.presence_of_element_located((By.ID, "tabSearchTab:txtSearch")),
        )
        campo_numproc.clear()
        sleep(0.15)
        campo_numproc.send_keys(numero_processo)
        self.driver.find_element(By.ID, "btnPesquisar").click()

        try:
            return self.open_proc()

        except TimeoutException:
            message = "Processo não encontrado!"
            type_log = "error"
            self.print_msg(
                message=message,
                type_log=type_log,
                row=self.row,
            )
            return False

        except StaleElementReferenceException:
            sleep(5)
            return self.open_proc()

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

    def screenshot_iframe(self, url_page: str, path_comprovante: Path) -> None:
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

    def open_proc(self) -> bool:
        open_proc = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((
                By.ID,
                "dtProcessoResults:0:btnProcesso",
            )),
        )
        if self.botname.upper() != "CADASTRO":
            if self.botname.upper() == "COMPLEMENTAR_CADASTRO":
                open_proc = self.driver.find_element(
                    By.ID,
                    "dtProcessoResults:0:btnEditar",
                )

            open_proc.click()

        message = "Processo encontrado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        return True
