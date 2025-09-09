"""Módulo para a classe de controle dos robôs PROJUDI."""

from __future__ import annotations

import platform
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import perf_counter, sleep
from typing import TYPE_CHECKING, ClassVar, Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import (
    raise_start_error,
)
from crawjud.controllers.main import CrawJUD
from crawjud.resources.elements import jusbr as el

if TYPE_CHECKING:
    from crawjud.custom.task import ContextTask
    from crawjud.interfaces.dict.bot import BotData

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

type MethodsSearch = Literal["peticionamento", "consulta"]


class JusBrBot[T](CrawJUD):
    """Classe Master para robôs do 'jus.br'."""

    navegação_guiada_checked: ClassVar[bool] = False

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
        """Realize a autenticação no sistema JusBR utilizando certificado digital.

        Returns:
            bool: Retorna True se a autenticação for bem-sucedida, caso contrário False.

        """
        logado = False

        driver = self.driver
        wait = self.wait

        driver.get(el.url_jusbr)

        sleep(5)

        btn_certificado = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                ('div[class="certificado"] > a'),
            )),
        )
        event_cert = btn_certificado.get_attribute("onclick")
        driver.execute_script(event_cert)

        sleep(5)

        wait._timeout = 30

        with suppress(Exception):
            wait.until(ec.url_contains(el.url_jusbr))
            logado = True

        return logado

    def search(self, method: MethodsSearch) -> bool:
        """Realize a busca de processo no JusBR conforme o método especificado.

        Args:
            method (MethodsSearch): Informe o método de busca, podendo ser
                "peticionamento" ou "consulta".

        Returns:
            bool: Retorna True se o processo for encontrado, caso contrário False.

        """
        self.driver.refresh()

        def navegacao_guiada() -> None:
            with suppress(Exception):
                btn_pular_nav_guiada = WebDriverWait(
                    driver,
                    30,
                ).until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="mat-dialog-0"]/app-confirm-dialog/mat-dialog-actions/button[1]',
                        ),
                    ),
                )
                btn_pular_nav_guiada.click()
                sleep(3)

                self.navegação_guiada_checked = True

        processo_encontrado = False

        with suppress(Exception):
            bot_data: BotData = self.bot_data
            driver = self.driver
            wait = self.wait
            url_dict = {
                "consulta": el.url_consultaprocesso,
                "peticionamento": el.url_peticionamento,
            }

            current_window = driver.current_window_handle

            url = url_dict[method]
            driver.get(url=url)

            if not self.navegação_guiada_checked:
                navegacao_guiada()

            input_processo = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.input_busca_processo,
                )),
            )

            input_processo.send_keys(bot_data["NUMERO_PROCESSO"])
            input_processo.send_keys(Keys.ENTER)

            table_processo = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.table_processo,
                )),
            )

            processo = table_processo.find_elements(
                By.TAG_NAME,
                el.tag_rows_table,
            )[0]

            if method == "peticionamento":
                btn_acao = processo.find_element(By.CSS_SELECTOR, el.btn_acao)
                if "Selecionar" in btn_acao.text:
                    btn_acao.click()

                    wait.until(
                        ec.presence_of_element_located((
                            By.XPATH,
                            el.text_info,
                        )),
                    )

                    table_processo = wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            el.table_processo,
                        )),
                    )

                    processo = table_processo.find_elements(
                        By.TAG_NAME,
                        el.tag_rows_table,
                    )[-1]

            processo.click()

            wait.until(ec.number_of_windows_to_be(2))

            new_window = list(
                filter(lambda x: x != current_window, driver.window_handles),
            )[-1]
            driver.close()
            driver.switch_to.window(new_window)

            processo_encontrado = True

        return processo_encontrado
