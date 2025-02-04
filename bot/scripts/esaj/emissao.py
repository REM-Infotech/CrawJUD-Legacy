"""
Module: emissao.

This module manages the emission processes within the CrawJUD-Bots application.
"""

import platform
import re
import time
from contextlib import suppress
from time import sleep

import requests
from pypdf import PdfReader
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ...common import ErroDeExecucao
from ...core import CrawJUD

# from ...shared import PropertiesCrawJUD
from ...Utils import OtherUtils

type_docscss = {
    "custas_iniciais": {
        "cnpj": [
            'input[name="entity.flTipoPessoa"][value="J"]',
            'tr[id="campoNuCnpj"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CNPJ"]',
        ],
        "cpf": [
            'input[name="entity.flTipoPessoa"][value="F"]',
            'tr[id="campoNuCpf"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CPF"]',
        ],
    },
    "preparo ri": {
        "cnpj": [
            'input[name="entity.flTipoPessoa"][value="J"]',
            'tr[id="campoNuCnpj"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CNPJ"]',
        ],
        "cpf": [
            'input[name="entity.flTipoPessoa"][value="F"]',
            'tr[id="campoNuCpf"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CPF"]',
        ],
    },
}


class Emissao(CrawJUD):
    """
    The Emissao class extends CrawJUD to handle emission tasks within the application.

    Attributes:
        attribute_name (type): Description of the attribute.
        # ...other attributes...
    """

    count_doc = OtherUtils.count_doc

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the Emissao instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # PropertiesCrawJUD.kwrgs = kwrgs
        # for key, value in list(kwrgs.items()):
        #     setattr(PropertiesCrawJUD, key, value)

        super().setup()
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """
        Execute the emission process.

        Raises:
            EmissionError: If an error occurs during emission.
        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                    old_message = self.message

                    self.auth_bot()

                if old_message is None:
                    old_message = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """
        Queue the emission tasks.

        Raises:
            ErroDeExecucao: If an error occurs during the queue process.
        """
        try:
            custa = str(self.bot_data.get("TIPO_GUIA"))
            if custa.lower() == "custas iniciais":
                self.tipodoc = custa
                self.custas_iniciais()

            elif custa.lower() == "preparo ri":
                custa = "Custas Preparo"
                self.tipodoc = custa
                self.preparo_ri()

            self.downloadpdf(self.generate_doc())
            self.append_success(self.get_barcode())

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def custas_iniciais(self) -> None:
        """Handle the initial costs emission process."""
        url_custas_ini = "".join(
            (
                "https://consultasaj.tjam.jus.br/ccpweb/iniciarCalculoDeCustas.do?",
                "cdTipoCusta=7&flTipoCusta=0&&cdServicoCalculoCusta=690003",
            )
        )

        self.driver.get(url_custas_ini)

        self.message = "Informando foro"
        self.type_log = "log"
        self.prt()

        set_foro: WebElement = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.ome_foro))
        )
        set_foro.send_keys(self.bot_data.get("FORO"))

        set_classe = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.tree_selection
        )
        set_classe.send_keys(self.bot_data.get("CLASSE"))

        semprecível = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.civil_selector
        )
        semprecível.click()

        val_acao = self.driver.find_element(By.CSS_SELECTOR, self.elements.valor_acao)
        val_acao.send_keys(self.bot_data.get("VALOR_CAUSA"))

        nameinteressado = self.driver.find_element(
            By.CSS_SELECTOR, 'input[name="entity.nmInteressado"]'
        )
        nameinteressado.send_keys(self.bot_data.get("NOME_INTERESSADO"))

        elements: list = type_docscss.get(self.bot_data.get("TIPO_GUIA")).get(
            self.count_doc(self.bot_data.get("CPF_CNPJ"))
        )
        set_doc = self.driver.find_element(By.CSS_SELECTOR, elements[0])
        set_doc.click()
        sleep(0.5)
        setcpf_cnpj = self.driver.find_element(
            By.CSS_SELECTOR, elements[1]
        ).find_element(By.CSS_SELECTOR, elements[2])
        sleep(0.5)
        setcpf_cnpj.send_keys(self.bot_data.get("CPF_CNPJ"))

        avançar = self.driver.find_element(By.CSS_SELECTOR, self.elements.botao_avancar)
        avançar.click()

        self.valor_doc = ""
        with suppress(TimeoutException):
            css_val_doc = self.elements.css_val_doc_custas_ini
            self.valor_doc: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_val_doc))
            ).text

    def preparo_ri(self) -> None:
        """
        Handle the preparation of RI emission process.

        Raises:
            ErroDeExecucao: If an error occurs during the preparation process.
        """
        portal = self.bot_data.get("PORTAL", "não informado")
        if str(portal).lower() == "esaj":
            self.driver.get(self.elements.url_preparo_esaj)

        elif str(portal).lower() == "projudi":
            self.driver.get(self.elements.url_preparo_projudi)

            set_foro: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.nome_foro)
                )
            )
            set_foro.send_keys(self.bot_data.get("FORO"))

            val_acao = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.valor_acao
            )
            val_acao.send_keys(self.bot_data.get("VALOR_CAUSA"))

            nameinteressado = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.interessado
            )
            nameinteressado.send_keys(self.bot_data.get("NOME_INTERESSADO"))

            elements: list = type_docscss.get(self.bot_data.get("TIPO_GUIA")).get(
                self.count_doc(self.bot_data.get("CPF_CNPJ"))
            )

            set_doc = self.driver.find_element(By.CSS_SELECTOR, elements[0])
            set_doc.click()
            sleep(0.5)
            setcpf_cnpj = self.driver.find_element(
                By.CSS_SELECTOR, elements[1]
            ).find_element(By.CSS_SELECTOR, elements[2])
            sleep(0.5)
            setcpf_cnpj.send_keys(self.bot_data.get("CPF_CNPJ"))

            avançar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_avancar
            )
            avançar.click()

            sleep(1)
            set_RI: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.check))
            )
            set_RI.click()

            sleep(1)
            last_avançar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_avancar_dois
            )
            last_avançar.click()

            sleep(1)
            css_val_doc = "body > table:nth-child(4) > tbody > tr > td > table:nth-child(10) > tbody > tr:nth-child(3) > td:nth-child(3) > strong"
            self.valor_doc: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_val_doc))
            ).text

        elif portal == "não informado":
            raise ErroDeExecucao(
                "Informar portal do processo na planilha (PROJUDI ou ESAJ)"
            )

    def renajud(self) -> None:
        """Handle the Renajud emission process."""
        pass

    def sisbajud(self) -> None:
        """Handle the Sisbajud emission process."""
        pass

    def custas_postais(self) -> None:
        """Handle the postal costs emission process."""
        pass

    def generate_doc(self) -> str:
        """
        Generate the document for emission.

        Returns:
            str: The URL of the generated document.

        Raises:
            ErroDeExecucao: If an error occurs during document generation.
        """
        self.original_window = original_window = self.driver.current_window_handle
        generatepdf: WebElement = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.boleto))
        )
        onclick_value = generatepdf.get_attribute("onclick")
        url_start = onclick_value.find("'") + 1
        url_end = onclick_value.find("'", url_start)
        url = onclick_value[url_start:url_end]
        sleep(0.5)
        # Store the ID of the original window

        sleep(0.5)
        self.driver.switch_to.new_window("tab")
        self.driver.get(f"https://consultasaj.tjam.jus.br{url}")
        sleep(2)

        # Checar se não ocorreu o erro "Boleto inexistente"
        check = None
        with suppress(TimeoutException):
            check: WebElement = (
                WebDriverWait(self.driver, 3)
                .until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.elements.mensagem_retorno)
                    )
                )
                .text
            )

        if check:
            self.driver.close()
            sleep(0.7)
            self.driver.switch_to.window(original_window)
            raise ErroDeExecucao("Esaj não gerou a guia")

        elif not check:
            return f"https://consultasaj.tjam.jus.br{url}"

    def downloadpdf(self, link_pdf):
        """
        Download the PDF document.

        Args:
            link_pdf (str): The URL of the PDF document.
        """
        response = requests.get(link_pdf, timeout=60)

        self.nomearquivo = f"{self.tipodoc} - {self.bot_data.get('NUMERO_PROCESSO')} - {self.nomeparte} - {self.pid}.pdf"

        if platform.system() == "Windows":
            self.path_pdf = path_pdf = f"{self.output_dir_path}\\{self.nomearquivo}"

        elif platform.system() == "Linux":
            self.path_pdf = path_pdf = f"{self.output_dir_path}/{self.nomearquivo}"

        with open(path_pdf, "wb") as file:
            file.write(response.content)

        self.driver.close()
        sleep(0.7)
        self.driver.switch_to.window(self.original_window)
        self.message = (
            f"Boleto Nº{self.bot_data.get('NUMERO_PROCESSO')} emitido com sucesso!"
        )
        self.type_log = "log"
        self.prt()

    def get_barcode(self) -> None:
        """
        Extract the barcode from the PDF document.

        Returns:
            list: A list containing barcode information.

        Raises:
            ErroDeExecucao: If an error occurs during barcode extraction.
        """
        try:
            self.message = "Extraindo código de barras"
            self.type_log = "log"
            self.prt()

            sleep(2)
            # Inicialize uma lista para armazenar os números encontrados
            bar_code = ""
            numeros_encontrados = []

            # Expressão regular para encontrar números nesse formato
            pattern = r"\b\d{5}\.\d{5}\s*\d{5}\.\d{6}\s*\d{5}\.\d{6}\s*\d\s*\d{14}\b"

            pdf_file = self.path_pdf
            read = PdfReader(pdf_file)

            # Read PDF
            for page in read.pages:
                text = page.extract_text()

                # Use a expressão regular para encontrar números
                numeros = re.findall(pattern, text)

                # Adicione os números encontrados à lista
                numeros_encontrados.extend(numeros)

            # Imprima os números encontrados
            for numero in numeros_encontrados:
                bar_code = numero.replace("  ", "")
                bar_code = bar_code.replace(" ", "")
                bar_code = bar_code.replace(".", " ")
                numero = numero.split("  ")
                numero = numero[2].split(".")

            return [
                self.bot_data.get("NUMERO_PROCESSO"),
                self.tipodoc,
                self.valor_doc,
                self.data_lancamento,
                "guias",
                "JEC",
                "SENTENÇA",
                bar_code,
                self.nomearquivo,
            ]

        except Exception as e:
            raise ErroDeExecucao(e=e)
