from time import sleep

from controllers.elaw import ElawBot
from resources.elements import elaw as el
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class ElawLocalidade(ElawBot):
    def localidade(self) -> None:
        message = "Informando localidade"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        localidade = self.bot_data.get("LOCALIDADE")

        input_localidade = self.driver.find_element(
            By.XPATH,
            el.localidade,
        )
        input_localidade.click()
        input_localidade.clear()
        input_localidade.send_keys(localidade)

        id_element = input_localidade.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.sleep_load('div[id="j_id_4p"]')

        message = "Localidade informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def esfera(self, text: str = "Judicial") -> None:
        text = "Judicial"

        message = "Informando esfera do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.css_esfera_judge)),
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Esfera Informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def estado(self) -> None:
        key = "ESTADO"

        text = str(self.bot_data.get(key, None))

        message = "Informando estado do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.estado_input)),
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Estado do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def comarca(self) -> None:
        text = str(self.bot_data.get("COMARCA"))

        message = "Informando comarca do processo"
        type_log = "log"

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.comarca_input)),
        )
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Comarca do processo informado!"
        type_log = "log"

        self.print_msg(message=message, type_log=type_log, row=self.row)

    def foro(self) -> None:
        text = str(self.bot_data.get("FORO"))

        message = "Informando foro do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.foro_input)),
        )
        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Foro do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def vara(self) -> None:
        text = self.bot_data.get("VARA")

        wait = self.wait
        message = "Informando vara do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.vara_input)),
        )

        element_select.select2(text)

        self.sleep_load('div[id="j_id_4p"]')

        message = "Vara do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def capital_interior(self) -> None:
        message = "Preenchendo UF Processo..."
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        element_select: WebElement = self.driver.find_element(
            By.XPATH,
            el.select_uf_proc,
        )
        text = str(self.bot_data.get("CAPITAL_INTERIOR"))
        element_select.select2(text)
        sleep(0.5)

        self.sleep_load('div[id="j_id_4p"]')

        if str(self.bot_data.get("CAPITAL_INTERIOR")).lower() == "outro estado":
            other_location: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_other_location,
                )),
                message="Erro ao encontrar elemento",
            )
            other_location.click()
            other_location.send_keys(self.bot_data.get("ESTADO"))
            other_location.send_keys(Keys.ENTER)

    def bairro(self) -> None:
        """Inform the neighborhood of the process.

        This method inputs the neighborhood information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando bairro"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        bairro_ = self.bot_data.get("BAIRRO")

        input_bairro = self.driver.find_element(
            By.XPATH,
            el.bairro_input,
        )
        input_bairro.click()
        input_bairro.clear()
        input_bairro.send_keys(bairro_)

        id_element = input_bairro.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.sleep_load('div[id="j_id_4p"]')

        message = "Bairro informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)
