from time import sleep
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from bots.elaw.master import ElawBot
from bots.resources.elements import elaw as el

if TYPE_CHECKING:
    from bots.resources.driver.web_element import WebElementBot
type_doc = {11: "cpf", 14: "cnpj"}


class ElawInformacaoInterna(ElawBot):
    def unidade_consumidora(self) -> None:
        message = "Informando unidade consumidora"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        input_uc: WebElementBot = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.css_input_uc,
            )),
        )
        input_uc.click()

        input_uc.clear()

        input_uc.send_keys(self.bot_data.get("UNIDADE_CONSUMIDORA"))

        message = "Unidade consumidora informada!"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def divisao(self) -> None:
        message = "Informando divisão"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        sleep(0.5)
        text = str(self.bot_data.get("DIVISAO"))
        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.divisao_select)),
        )
        element_select.select2(text)

        self.sleep_load('div[id="j_id_4p"]')

        message = "Divisão informada!"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )
