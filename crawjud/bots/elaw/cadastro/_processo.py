from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.controllers.elaw import ElawBot
from crawjud.custom.task import ContextTask as ContextTask
from crawjud.decorators import shared_task as shared_task
from crawjud.decorators.bot import wrap_cls as wrap_cls
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot as WebElement


class ElawInformacoesProcesso(ElawBot):
    def proceso(self) -> None:
        key = "NUMERO_PROCESSO"
        css_campo_processo = el.numero_processo

        message = "Informando número do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        campo_processo: WebElement = self.wait.until(
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
        self.sleep_load('div[id="j_id_4b"]')

        message = "Número do processo informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def area_direito(self) -> None:
        wait = self.wait
        message = "Informando área do direito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        text = str(self.bot_data.get("AREA_DIREITO"))
        sleep(0.5)

        element_area_direito: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.css_label_area,
            )),
        )
        element_area_direito.select2(text)
        self.sleep_load('div[id="j_id_47"]')

        message = "Área do direito selecionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def subarea_direito(self) -> None:
        wait = self.wait
        message = "Informando sub-área do direito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        text = str(self.bot_data.get("SUBAREA_DIREITO"))
        sleep(0.5)

        element_subarea: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.comboareasub_css,
            )),
        )
        element_subarea.select2(text)

        self.sleep_load('div[id="j_id_4b"]')
        message = "Sub-Área do direito selecionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def fase(self) -> None:
        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.fase_input)),
        )
        text = self.bot_data.get("FASE")

        message = "Informando fase do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.sleep_load('div[id="j_id_48"]')

        message = "Fase informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def provimento(self) -> None:
        text = self.bot_data.get("PROVIMENTO")
        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.provimento_input)),
        )

        message = "Informando provimento antecipatório"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.sleep_load('div[id="j_id_48"]')

        message = "Provimento antecipatório informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def fato_gerador(self) -> None:
        message = "Informando fato gerador"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.fato_gerador_input)),
        )

        text = self.bot_data.get("FATO_GERADOR")

        element_select.select2(text)
        self.sleep_load('div[id="j_id_48"]')

        message = "Fato gerador informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

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
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.objeto_input)),
        )
        text = self.bot_data.get("OBJETO")

        element_select.select2(text)
        self.sleep_load('div[id="j_id_48"]')

        message = "Objeto do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def acao(self) -> None:
        message = "Informando ação do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        div_comboProcessoTipo: WebElement = self.wait.until(  # noqa: N806
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
        self.sleep_load('div[id="j_id_4b"]')

        message = "Ação informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)
