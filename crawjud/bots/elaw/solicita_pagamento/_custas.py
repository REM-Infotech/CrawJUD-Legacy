"""Module for managing payment solution processes within the ELAW system.

This module provides functionality to handle payment management and solution creation within
the ELAW system. It enables automated payment processing, validations, and record-keeping.

Classes:
    SolPags: Handles payment solutions by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.controllers.elaw import ElawBot
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver import WebElementBot as WebElement
type_doc = {11: "cpf", 14: "cnpj"}


class ElawCustas(ElawBot):
    def custas(self) -> None:
        message = "Informando valor da guia"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        valor_doc = self.bot_data.get("VALOR_GUIA").replace(".", ",")

        element: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.valor_guia)),
        )
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        sleep(0.5)
        element.send_keys(Keys.BACK_SPACE)
        sleep(0.5)
        element.send_keys(valor_doc)

        self.driver.execute_script(
            f"document.querySelector('{el.valor_guia}').blur()",
        )

        sleep(0.5)

        list_tipo_doc: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.type_doc_css)),
        )
        list_tipo_doc.click()
        sleep(1)

        set_gru = self.driver.find_element(By.CSS_SELECTOR, el.css_gru)
        set_gru.click()

        sleep(2)
        message = "Inserindo documento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        docs = [self.bot_data.get("DOC_GUIA")]

        for doc in docs:
            doc = self.format_string(doc)
            insert_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.editar_pagamento,
                )),
            )
            insert_doc.send_keys(f"{self.output_dir_path}/{doc}")

            wait_upload: WebElement = (
                WebDriverWait(self.driver, 20)
                .until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.editar_pagamentofile,
                    )),
                )
                .find_element(By.TAG_NAME, "table")
                .find_element(By.TAG_NAME, "tbody")
                .find_elements(By.TAG_NAME, "tr")
            )

            if len(wait_upload) == len(docs):
                break

        solicitante = str(self.bot_data.get("SOLICITANTE")).lower()
        if solicitante == "monitoria" or solicitante.lower() == "monitória":
            desc_pgto: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_desc_pgto,
                )),
            )
            desc_pgto.send_keys(self.bot_data.get("DESC_PAGAMENTO"))
            self.driver.execute_script(
                f"document.querySelector('{el.css_desc_pgto}').blur()",
            )

        message = "Informando tipo de guia"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        sleep(1)

        tipo_guia = str(self.bot_data.get("TIPO_GUIA"))
        list_tipo_custa: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_listcusta,
            )),
        )
        self.select2_elaw(list_tipo_custa, tipo_guia)

        sleep(1)
        message = "Informando data para pagamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        data_vencimento = self.driver.find_element(
            By.CSS_SELECTOR,
            el.css_data,
        )
        data_vencimento.click()
        data_vencimento.send_keys(self.bot_data.get("DATA_LANCAMENTO"))
        self.driver.execute_script(
            f"document.querySelector('{el.css_data}').blur()",
        )
        self.interact.sleep_load('div[id="j_id_2x"]')

        label_forma_pgto = self.driver.find_element(
            By.CSS_SELECTOR,
            el.valor_processo,
        )
        label_forma_pgto.click()

        sleep(1)
        boleto = self.driver.find_element(By.CSS_SELECTOR, el.boleto)
        boleto.click()

        self.interact.sleep_load('div[id="j_id_2x"]')

        campo_cod_barras: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.css_cod_bars)),
        )
        campo_cod_barras.click()
        sleep(0.5)
        campo_cod_barras.send_keys(self.bot_data.get("COD_BARRAS"))
        self.driver.execute_script(
            f"document.querySelector('{el.css_cod_bars}').blur()",
        )

        message = "Informando favorecido"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        sleep(2)
        input_favorecido: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_inputfavorecido,
            )),
        )
        input_favorecido.click()
        sleep(1)
        input_favorecido.clear()

        input_favorecido.send_keys(
            self.bot_data.get("CNPJ_FAVORECIDO", "04.812.509/0001-90"),
        )

        result_favorecido: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.resultado_favorecido,
            )),
        )
        result_favorecido.click()
        self.driver.execute_script(
            f"document.querySelector('{el.css_inputfavorecido}').blur()",
        )

        message = "Informando centro de custas"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        sleep(1)

        centro_custas: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_centro_custas,
            )),
        )
        centro_custas.click()
        centro_custas.send_keys("A906030100")

        message = "Informando conta débito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        div_conta_debito: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_div_conta_debito,
            )),
        )
        div_conta_debito.click()
        sleep(1)

        if solicitante == "jec":
            conta_debito = self.driver.find_element(
                By.CSS_SELECTOR,
                el.custas_civis,
            )
            conta_debito.click()

        elif solicitante == "monitoria" or solicitante == "monitória":
            conta_debito = self.driver.find_element(
                By.CSS_SELECTOR,
                el.custas_monitorias,
            )
            conta_debito.click()
