from contextlib import suppress

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from bots.resources.driver.web_element import WebElementBot
from bots.resources.elements import elaw as el
from common._raises import raise_execution_error

from ._interno import ElawInformacaoInterna
from ._localidade import ElawLocalidade
from ._partes import ElawPartesPrincipais
from ._processo import ElawInformacoesProcesso
from ._representantes import ElawRepresentantes
from ._valida import ElawValidacao
from ._valor import ElawValores


class ElawCadastro(
    ElawInformacaoInterna,
    ElawLocalidade,
    ElawPartesPrincipais,
    ElawRepresentantes,
    ElawValores,
    ElawInformacoesProcesso,
    ElawValidacao,
):
    def next_page(self) -> None:
        next_page: WebElementBot = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_button,
            )),
            message="Erro ao encontrar elemento",
        )
        next_page.click()

    def confirm_save(self) -> bool:
        wait = self.wait
        driver = self.driver
        msg_erro = "Cadastro do processo nao finalizado, verificar manualmente"
        with suppress(TimeoutException):
            WebDriverWait(driver, 20).until(
                ec.url_to_be(
                    "https://amazonas.elaw.com.br/processoView.elaw",
                ),
                message="Erro ao encontrar elemento",
            )

            self.print_message(
                message="Processo salvo com sucesso!",
                message_type="log",
            )
            return True

        with suppress(TimeoutException, NoSuchElementException):
            msg_erro = (
                wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.div_messageerro_css,
                    )),
                    message="Erro ao encontrar elemento",
                )
                .find_element(By.TAG_NAME, "ul")
                .text
            )

        return raise_execution_error(msg_erro)

    def salvar_tudo(self) -> None:
        wait = self.wait

        self.sleep_load('div[id="j_id_4p"]')
        salvartudo: WebElementBot = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_salvar_proc,
            )),
            message="Erro ao encontrar elemento",
        )

        message = "Salvando processo novo"
        message_type = "info"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        salvartudo.click()
