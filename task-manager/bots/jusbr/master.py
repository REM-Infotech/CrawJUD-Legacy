"""Módulo para a classe de controle dos robôs PROJUDI."""

from contextlib import suppress
from time import sleep
from typing import ClassVar

from __types import MethodsSearch
from resources.elements import jusbr as el
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from bots.head import CrawJUD


class JusBrBot(CrawJUD):
    """Classe Master para robôs do 'jus.br'."""

    navegação_guiada_checked: ClassVar[bool] = False

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
            bot_data: dict = self.bot_data
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
