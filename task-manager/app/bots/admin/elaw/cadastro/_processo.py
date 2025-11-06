from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from app.bots.controller.elaw import ElawBot
from app.bots.resources.driver.web_element import WebElementBot
from app.bots.resources.elements import elaw as el


class ElawInformacoesProcesso(ElawBot):
    def proceso(self) -> None:
        key = "NUMERO_PROCESSO"
        css_campo_processo = el.numero_processo

        message = "Informando número do processo"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        campo_processo: WebElementBot = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                css_campo_processo,
            )),
            message="Erro ao encontrar elemento",
        )
        campo_processo.click()

        campo_processo.send_keys(self.bot_data.get(key))

        self.driver.execute_script(
            f'document.querySelector("{css_campo_processo}").blur()',
        )
        self.sleep_load('div[id="j_id_4p"]')

        message = "Número do processo informado!"
        message_type = "info"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def area_direito(self) -> None:
        wait = self.wait
        message = "Informando área do direito"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )
        text = str(self.bot_data.get("AREA_DIREITO"))
        sleep(0.5)

        element_area_direito: WebElementBot = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.css_label_area,
            )),
        )
        element_area_direito.select2(text)
        self.sleep_load('div[id="j_id_47"]')

        message = "Área do direito selecionada!"
        message_type = "info"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def subarea_direito(self) -> None:
        wait = self.wait
        message = "Informando sub-área do direito"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        text = str(self.bot_data.get("SUBAREA_DIREITO"))
        sleep(0.5)

        element_subarea: WebElementBot = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.comboareasub_css,
            )),
        )
        element_subarea.select2(text)

        self.sleep_load('div[id="j_id_4p"]')
        message = "Sub-Área do direito selecionada!"
        message_type = "info"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def fase(self) -> None:
        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.fase_input)),
        )
        text = self.bot_data.get("FASE")

        message = "Informando fase do processo"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Fase informada!"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def provimento(self) -> None:
        text = self.bot_data.get("PROVIMENTO")
        element_select = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.provimento_input,
            )),
        )

        message = "Informando provimento antecipatório"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Provimento antecipatório informado!"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def fato_gerador(self) -> None:
        message = "Informando fato gerador"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        element_select = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.fato_gerador_input,
            )),
        )

        text = self.bot_data.get("FATO_GERADOR")

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Fato gerador informado!"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def desc_objeto(self) -> None:
        input_descobjeto = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.input_descobjeto,
            )),
        )
        input_descobjeto.click()

        text = self.bot_data.get("DESC_OBJETO")

        input_descobjeto.clear()
        input_descobjeto.send_keys(text)

        id_element = input_descobjeto.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

    def objeto(self) -> None:
        message = "Informando objeto do processo"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.objeto_input)),
        )
        text = self.bot_data.get("OBJETO")

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Objeto do processo informado!"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def acao(self) -> None:
        message = "Informando ação do processo"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        div_comboProcessoTipo: WebElementBot = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.combo_processo_tipo,
            )),
            message="Erro ao encontrar elemento",
        )
        div_comboProcessoTipo.click()

        elemento = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.filtro_processo,
            )),
            message="Erro ao encontrar elemento",
        )

        text = self.bot_data.get("ACAO")
        elemento.click()
        elemento.send_keys(text)
        elemento.send_keys(Keys.ENTER)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Ação informada!"
        message_type = "info"
        self.print_message(
            message=message,
            message_type=message_type,
        )
