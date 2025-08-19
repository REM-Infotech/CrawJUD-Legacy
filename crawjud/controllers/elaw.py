"""Módulo para a classe de controle dos robôs Elaw."""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.master import CrawJUD
from crawjud.resources.elements import esaj as el

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class ElawBot[T](CrawJUD):
    """Classe de controle para robôs do Elaw."""

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
        """Procura processo no ESAJ.

        Returns:
           bool: True se encontrado; ou False
        Navega pela pagina do ESAJ, processa entradas com base no grau do processo.

        Raises:
            ExecutionError:
                Erro de execução

        """
        self.bot_data = bot_data
        grau = self.bot_data.get("GRAU", 1)
        id_consultar = "botaoConsultarProcessos"
        if grau == 2:
            self.driver.get(el.consultaproc_grau2)
            id_consultar = "pbConsultar"

        elif not grau or grau != 1 or grau != 2:
            raise ExecutionError(message="Informar instancia!")

        sleep(1)
        # Coloca o campo em formato "Outros" para inserir o número do processo
        ratioNumberOld = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((By.ID, "radioNumeroAntigo")),
        )
        ratioNumberOld.click()

        # Insere o processo no Campo
        lineprocess = self.wait.until(
            ec.presence_of_element_located((
                By.ID,
                "nuProcessoAntigoFormatado",
            )),
        )
        lineprocess.click()
        lineprocess.send_keys(self.bot_data.get("NUMERO_PROCESSO"))

        # Abre o Processo
        openprocess = None
        with suppress(TimeoutException):
            openprocess = self.wait.until(
                ec.presence_of_element_located((By.ID, id_consultar)),
            )
            openprocess.click()

        check_process = None
        with suppress(NoSuchElementException, TimeoutException):
            check_process = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "#numeroProcesso",
                )),
            )

        # Retry 1
        if not check_process:
            with suppress(NoSuchElementException, TimeoutException):
                check_process = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'div[id="listagemDeProcessos"]',
                    )),
                )

                if check_process:
                    check_process = (
                        check_process.find_element(By.TAG_NAME, "ul")
                        .find_elements(By.TAG_NAME, "li")[0]
                        .find_element(By.TAG_NAME, "a")
                    )

                    url_proc = check_process.get_attribute("href")
                    self.driver.get(url_proc)

        # Retry 2
        if not check_process:
            with suppress(NoSuchElementException, TimeoutException):
                check_process = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            'div.modal__process-choice > input[type="radio"]',
                        ),
                    ),
                )

                if check_process:
                    check_process.click()
                    btEnviarIncidente = self.driver.find_element(  # noqa: N806
                        By.CSS_SELECTOR,
                        'input[name="btEnviarIncidente"]',
                    )
                    btEnviarIncidente.click()

        return check_process is not None

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
