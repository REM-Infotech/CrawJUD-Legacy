from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app.resources.elements import elaw as el
from app.resources.search._main import SearchBot

if TYPE_CHECKING:
    from app.resources.driver.web_element import WebElementBot


class ElawSearch(SearchBot):
    def __call__(self) -> bool:
        numero_processo = self.bot_data.get("NUMERO_PROCESSO")
        message = f"Buscando processo {numero_processo}"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        self.driver.implicitly_wait(5)

        if self.driver.current_url != el.LINK_PROCESSO_LIST:
            self.driver.get(el.LINK_PROCESSO_LIST)

        campo_numproc: WebElementBot = self.wait.until(
            ec.presence_of_element_located((
                By.ID,
                "tabSearchTab:txtSearch",
            )),
        )
        campo_numproc.clear()
        sleep(0.15)
        campo_numproc.send_keys(numero_processo)
        self.driver.find_element(By.ID, "btnPesquisar").click()

        try:
            return self.open_proc()

        except TimeoutException:
            message = "Processo não encontrado!"
            message_type = "error"
            self.print_message(
                message=message,
                message_type=message_type,
            )
            return False

        except StaleElementReferenceException:
            sleep(5)
            return self.open_proc()

    def open_proc(self) -> bool:
        open_proc = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((
                By.ID,
                "dtProcessoResults:0:btnProcesso",
            )),
        )
        if self.config["categoria"].upper() != "CADASTRO":
            if self.config["categoria"].upper() == "COMPLEMENTAR_CADASTRO":
                open_proc = self.driver.find_element(
                    By.ID,
                    "dtProcessoResults:0:btnEditar",
                )

            open_proc.click()

        message = "Processo encontrado!"
        message_type = "info"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        return True
