"""Module for managing registration completion tasks in the ELAW system.

This module handles the completion and supplementation of registration data within the ELAW
system. It automates the process of filling in missing or additional registration details.

Classes:
    Complement: Manages registration completion by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)
    campos_validar (list): Fields to validate during registration completion

"""

from __future__ import annotations

import time
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.bots.elaw.cadastro import ElawCadastro
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls

if TYPE_CHECKING:
    from crawjud.utils.webdriver import WebElementBot as WebElement
type_doc = {11: "cpf", 14: "cnpj"}


@shared_task(name="elaw.complementar_cadastro", bind=True, context=ContextTask)
@wrap_cls
class Complement(ElawCadastro):
    """A class that configures and retrieves an elements bot instance.

    This class interacts with the ELAW system to complete the registration of a process.
    """

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elaw_formats(value)

            if self.event_stop_bot.is_set():
                self.success = self.total_rows - pos
                break

            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        """Execute the queue process for complementing registration.

        This method performs a series of operations to complete the registration
        process using the ELAW system. It checks the current search status, formats
        the bot data, and if the process is found, it initializes the registration
        complement by interacting with various web elements. The method logs the
        steps, calculates the execution time, and handles potential exceptions
        during the process.

        """
        try:
            search = self.search(bot_data=self.bot_data)

            if not search:
                self.print_msg(
                    message="Processo não encontrado",
                    type_log="error",
                    row=self.row,
                )

                return

            start_time = time.perf_counter()
            message = "Inicializando complemento de cadastro"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            lista1 = list(self.bot_data.keys())
            check_esfera = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.label_esfera,
                )),
            )
            esfera_xls = self.bot_data.get("ESFERA")

            if esfera_xls and check_esfera.text.lower() != esfera_xls.lower():
                self.esfera(self, esfera_xls)

            for item in lista1:
                func = getattr(self, item.lower(), None)

                if func and item.lower() != "esfera":
                    func()

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            calc = execution_time / 60
            splitcalc = str(calc).split(".")
            minutes = int(splitcalc[0])
            seconds = int(float(f"0.{splitcalc[1]}") * 60)

            self.validar_campos()
            self.validar_advs_participantes()
            self.salva_tudo()

            if self.confirm_save() is True:
                name_comprovante = self.print_comprovante()
                message = "Processo salvo com sucesso!"

            self.append_success(
                [
                    self.bot_data.get("NUMERO_PROCESSO"),
                    message,
                    name_comprovante,
                ],
                message,
            )

            message = f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

        except Exception as e:
            self.append_error(exc=e)

    def print_comprovante(self) -> str:
        """Print the comprovante (receipt) of the registration.

        This method captures a screenshot of the process and saves it
        as a comprovante file.

        Returns
        -------
        str
            The name of the comprovante file.

        """
        name_comprovante = f"Comprovante Cadastro - {self.bot_data.get('NUMERO_PROCESSO')} - PID {self.pid}.png"
        savecomprovante = (
            Path(self.output_dir_path).resolve().joinpath(name_comprovante)
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante

    def unidade_consumidora(self) -> None:
        """Handle the process of informing the consumer unit in the web application.

        This function performs the following steps:
        1. Logs the start of the process.
        2. Waits for the input field for the consumer unit to be present in the DOM.
        3. Clicks on the input field.
        4. Clears any existing text in the input field.
        5. Sends the consumer unit data to the input field.
        6. Logs the completion of the process.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando unidade consumidora"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        input_uc: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                self.elements.css_input_uc,
            )),
        )
        input_uc.click()

        self.interact.clear(input_uc)

        self.interact.send_key(
            input_uc,
            self.bot_data.get("UNIDADE_CONSUMIDORA"),
        )

        message = "Unidade consumidora informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def localidade(self) -> None:
        """Inform the locality of the process.

        This method inputs the locality information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando localidade"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        localidade = self.bot_data.get("LOCALIDADE")

        input_localidade = self.driver.find_element(
            By.XPATH,
            self.elements.localidade,
        )
        input_localidade.click()
        self.interact.clear(input_localidade)
        self.interact.send_key(input_localidade, localidade)

        id_element = input_localidade.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Localidade informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

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
            self.elements.bairro_input,
        )
        input_bairro.click()
        self.interact.clear(input_bairro)
        self.interact.send_key(input_bairro, bairro_)

        id_element = input_bairro.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Bairro informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def divisao(self) -> None:
        """Inform the division of the process.

        This method inputs the division information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando divisão"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        sleep(0.5)
        text = str(self.bot_data.get("DIVISAO"))
        element_select = self.elements.divisao_select
        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )

        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Divisão informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def data_citacao(self) -> None:
        """Inform the citation date in the process.

        This method inputs the citation date into the system and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando data de citação"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        data_citacao: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                self.elements.data_citacao,
            )),
        )
        self.interact.clear(data_citacao)
        self.interact.sleep_load('div[id="j_id_48"]')
        self.interact.send_key(data_citacao, self.bot_data.get("DATA_CITACAO"))
        sleep(2)
        id_element = data_citacao.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Data de citação informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def fase(self) -> None:
        """Inform the phase of the process.

        This method inputs the phase information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        element_select = self.elements.fase_input
        text = self.bot_data.get("FASE")

        message = "Informando fase do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Fase informada!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def provimento(self) -> None:
        """Inform the anticipatory provision in the process.

        This method inputs the anticipatory provision information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        text = self.bot_data.get("PROVIMENTO")
        element_select = self.elements.provimento_input

        message = "Informando provimento antecipatório"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Provimento antecipatório informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def valor_causa(self) -> None:
        """Inform the value of the cause.

        This method inputs the value of the cause into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando valor da causa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        valor_causa: WebElement = self.wait.until(
            ec.element_to_be_clickable((By.XPATH, self.elements.valor_causa)),
            message="Erro ao encontrar elemento",
        )

        valor_causa.click()
        sleep(0.5)
        valor_causa.clear()

        self.interact.send_key(valor_causa, self.bot_data.get("VALOR_CAUSA"))

        id_element = valor_causa.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Valor da causa informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def fato_gerador(self) -> None:
        """Inform the triggering event (fato gerador).

        This method inputs the triggering event information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando fato gerador"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select = self.elements.fato_gerador_input

        text = self.bot_data.get("FATO_GERADOR")

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Fato gerador informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def desc_objeto(self) -> None:
        """Fill in the description object field.

        This method inputs the description of the object into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        input_descobjeto = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                self.elements.input_descobjeto,
            )),
        )
        self.interact.click(input_descobjeto)

        text = self.bot_data.get("DESC_OBJETO")

        self.interact.clear(input_descobjeto)
        self.interact.send_key(input_descobjeto, text)

        id_element = input_descobjeto.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

    def objeto(self) -> None:
        """Inform the object of the process.

        This method inputs the object information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando objeto do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select = self.elements.objeto_input
        text = self.bot_data.get("OBJETO")

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Objeto do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def tipo_empresa(self) -> None:
        """Set the type of company and update relevant UI elements.

        This method determines the type of company (either "Ativa" or "Passiva") based on the
        "TIPO_EMPRESA" value in `self.bot_data`. It then updates the UI elements for
        contingencia and tipo_polo with the appropriate values and logs the actions performed.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        message = "Informando contingenciamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                self.elements.contingencia,
            )),
        )

        text = ["Passiva", "Passivo"]
        if str(self.bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        self.select2_elaw(element_select, text[0])
        self.interact.sleep_load('div[id="j_id_48"]')

        element_select = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                self.elements.tipo_polo,
            )),
        )

        text = ["Passiva", "Passivo"]
        if str(self.bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        self.select2_elaw(element_select, text[1])
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Contingenciamento informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def escritorio_externo(self) -> None:
        """Inform the external office involved in the process.

        This method retrieves the external office information from the bot data,
        inputs it into the designated field, and logs the action performed.

        """
        message = "Informando Escritório Externo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        driver = self.driver
        _wait = self.wait
        elements = self.elements

        sleep(1)

        text = self.bot_data.get("ESCRITORIO_EXTERNO")

        element_select = driver.find_element(
            By.XPATH,
            elements.select_escritorio,
        )

        self.interact.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Escritório externo informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)
