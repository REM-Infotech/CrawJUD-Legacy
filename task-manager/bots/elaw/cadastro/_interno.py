from time import sleep
from typing import TYPE_CHECKING

from resources.elements import elaw as el
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from .master import ElawBot

if TYPE_CHECKING:
    from app.utils.webdriver import WebElementBot as WebElement
type_doc = {11: "cpf", 14: "cnpj"}


class ElawInformacaoInterna(ElawBot):
    def unidade_consumidora(self) -> None:
        message = "Informando unidade consumidora"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        input_uc: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.css_input_uc,
            )),
        )
        input_uc.click()

        input_uc.clear()

        input_uc.send_keys(self.bot_data.get("UNIDADE_CONSUMIDORA"))

        message = "Unidade consumidora informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def divisao(self) -> None:
        message = "Informando divisão"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        sleep(0.5)
        text = str(self.bot_data.get("DIVISAO"))
        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.divisao_select)),
        )
        element_select.select2(text)

        self.sleep_load('div[id="j_id_4p"]')

        message = "Divisão informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
