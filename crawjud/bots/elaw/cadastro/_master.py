from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError as ExecutionError
from crawjud.custom.task import ContextTask as ContextTask
from crawjud.decorators import shared_task as shared_task
from crawjud.decorators.bot import wrap_cls as wrap_cls
from crawjud.resources.elements import elaw as el

from ._interno import ElawInformacaoInterna
from ._localidade import ElawLocalidade
from ._partes import ElawPartesPrincipais
from ._processo import ElawInformacoesProcesso
from ._representantes import ElawRepresentantes
from ._valida import ElawValidacao
from ._valor import ElawValores

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot as WebElement


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
        next_page: WebElement = self.wait.until(
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
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
                message="Erro ao encontrar elemento",
            )

            self.print_msg(
                message="Processo salvo com sucesso!",
                type_log="log",
                row=self.row,
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

        return _raise_execution_error(msg_erro)

    def salvar_tudo(self) -> None:
        wait = self.wait

        self.sleep_load('div[id="j_id_4b"]')
        salvartudo: WebElement = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_salvar_proc,
            )),
            message="Erro ao encontrar elemento",
        )

        message = "Salvando processo novo"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        salvartudo.click()
