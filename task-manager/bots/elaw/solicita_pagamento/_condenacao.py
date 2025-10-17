"""Module for managing payment solution processes within the ELAW system.

This module provides functionality to handle payment management and solution creation within
the ELAW system. It enables automated payment processing, validations, and record-keeping.

Classes:
    SolPags: Handles payment solutions by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

from time import sleep
from typing import TYPE_CHECKING

from resources.elements import elaw as el
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from bots.elaw.master import ElawBot

if TYPE_CHECKING:
    from app.utils.webdriver import WebElementBot as WebElement

type_doc = {11: "cpf", 14: "cnpj"}


class ElawCondenacao(ElawBot):
    def condenacao(self) -> None:
        message = "Informando o valor da guia"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        text = self.bot_data.get("VALOR_GUIA")
        element: WebElement = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, el.css_element)),
        )

        sleep(0.5)
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        self.interact.send_key(element, text)
        self.driver.execute_script(
            f"document.querySelector('{el.css_element}').blur()",
        )

        self.interact.sleep_load('div[id="j_id_2x"]')

        div_type_doc: WebElement = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, el.type_doc_css)),
        )
        div_type_doc.click()
        sleep(0.5)

        list_type_doc: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.list_type_doc_css,
            )),
        )
        list_type_doc = list_type_doc.find_elements(By.TAG_NAME, "li")

        for item in list_type_doc:
            item: WebElement = item
            if item.text.lower() == "guia de pagamento":
                item.click()
                break

        self.interact.sleep_load('div[id="j_id_2x"]')
        message = "Enviando guia"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        docs = [self.bot_data.get("DOC_GUIA")]
        calculo = self.bot_data.get("DOC_CALCULO", None)

        if calculo:
            calculos = [str(calculo)]

            if "," in str(calculo):
                calculos = str(calculo).split(",")

            docs.extend(calculos)

        for doc in docs:
            doc = self.format_string(doc.upper())
            insert_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.editar_pagamento,
                )),
            )
            path_doc = self.output_dir_path.joinpath(doc)
            insert_doc.send_keys(path_doc)

            self.interact.wait_fileupload()
            sleep(0.5)

        message = "Informando tipo de condenação"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        div_condenacao_type: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_div_condenacao_type,
            )),
        )
        div_condenacao_type.click()

        tipo_condenacao = str(self.bot_data.get("TIPO_CONDENACAO"))
        if tipo_condenacao.lower() == "sentença":
            sleep(0.5)
            sentenca = self.driver.find_element(
                By.CSS_SELECTOR,
                el.valor_sentenca,
            )
            sentenca.click()

        elif tipo_condenacao.lower() == "acórdão":
            sleep(0.5)
            acordao = self.driver.find_element(
                By.CSS_SELECTOR,
                el.valor_acordao,
            )
            acordao.click()

        message = "Informando descrição do pagamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        desc_pagamento = str(self.bot_data.get("DESC_PAGAMENTO"))

        desc_pgto: WebElement = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, el.css_desc_pgto)),
        )
        desc_pgto.click()
        if "\n" in desc_pagamento:
            desc_pagamento = desc_pagamento.replace("\n", "")

        elif "\t" in desc_pagamento:
            desc_pagamento = desc_pagamento.replace("\t", "")
        desc_pgto.send_keys(desc_pagamento)
        sleep(0.5)

        self.driver.execute_script(
            f"document.querySelector('{el.css_desc_pgto}').blur()",
        )

        message = "Informando data para pagamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        data_lancamento: WebElement = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, el.css_data)),
        )
        data_lancamento.click()
        data_lancamento.send_keys(self.bot_data.get("DATA_LANCAMENTO"))
        data_lancamento.send_keys(Keys.TAB)
        self.driver.execute_script(
            f"document.querySelector('{el.css_data}').blur()",
        )

        self.interact.sleep_load('div[id="j_id_2x"]')
        message = "Informando favorecido"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        input_favorecido: WebElement = WebDriverWait(self.driver, 10).until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_inputfavorecido,
            )),
        )
        input_favorecido.click()
        input_favorecido.clear()
        sleep(2)

        input_favorecido.send_keys(
            self.bot_data.get("CNPJ_FAVORECIDO", "00.360.305/0001-04"),
        )

        result_favorecido: WebElement = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.resultado_favorecido,
            )),
        )
        result_favorecido.click()

        self.interact.sleep_load('div[id="j_id_2x"]')
        message = "Informando forma de pagamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

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
            ec.element_to_be_clickable((By.CSS_SELECTOR, el.css_cod_bars)),
        )
        campo_cod_barras.click()
        sleep(0.5)

        cod_barras = str(self.bot_data.get("COD_BARRAS"))
        campo_cod_barras.send_keys(
            cod_barras.replace("\t", "").replace("\n", ""),
        )
        self.driver.execute_script(
            f"document.querySelector('{el.css_cod_bars}').blur()",
        )

        self.interact.sleep_load('div[id="j_id_2x"]')
        message = "Informando centro de custas"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        centro_custas: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_centro_custas,
            )),
        )
        centro_custas.click()
        centro_custas.send_keys("A906030100")

        self.driver.execute_script(
            f"document.querySelector('{el.css_centro_custas}').blur()",
        )

        sleep(1)
        message = "Informando conta para débito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        div_conta_debito: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_div_conta_debito,
            )),
        )
        div_conta_debito.click()
        sleep(1)
        conta_debito = self.driver.find_element(
            By.CSS_SELECTOR,
            'li[data-label="AMAZONAS - PAGTO CONDENAÇÕES DE LITÍGIOS CÍVEIS CONTRAPARTIDA"]',
        )
        conta_debito.click()
