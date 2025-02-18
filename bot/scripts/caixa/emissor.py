"""Module: emissor.

This module handles the emission of judicial deposit documents within the
Caixa system of the CrawJUD-Bots application. It provides functionalities
to manage accessing the site, filling forms, generating, and downloading
judicial deposit PDFs.

"""

import os
import re
import shutil
import time
from contextlib import suppress
from time import sleep
from typing import Self

from pypdf import PdfReader
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from ...common import ExecutionError
from ...core import CrawJUD
from ...Utils import OtherUtils


class Emissor(CrawJUD):  # noqa: N801
    """Class Emissor.

    Manages the emission, naming, barcode retrieval, and processing
    of judicial deposit documents within the Caixa system.

    Attributes:
        count_doc (callable): Utility method to decide the
            document type (CPF/CNPJ).

    """

    count_doc = OtherUtils.count_doc

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize an Emissor bot instance.

        Args:
            *args: Variable length argument list representing
                parameters necessary for the bot.
            **kwargs: Arbitrary keyword arguments containing
                configuration for the bot.

        Returns:
            Emissor: A new instance of the Emissor bot.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Create a new Emissor instance.

        Sets up initial variables, including authentication and timing.
        Calls setup() to configure the environment and auth_bot() to
        perform the required login flow.

        Args:
            *args: The arguments needed for the bot.
            **kwargs: Additional keyword arguments.

        """
        super().__init__()

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Run the main processing loop.

        Iterates over the DataFrame rows, handling session checks and
        errors. Logs any encountered exception, then restarts or stops
        as needed.
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
                        self.driver_launch(message="Webdriver encerrado inesperadamente, reinicializando...")

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
        """Manage the processing queue steps.

        Orchestrates the following emission steps:
        site navigation, locale selection, deposit data input,
        document creation, and PDF renaming. Handles exceptions
        gracefully by raising ExecutionError.
        """
        try:
            nameboleto = None
            self.get_site()
            self.locale_proc()
            self.proc_nattribut()
            self.dados_partes()
            self.info_deposito()
            self.make_doc()
            nameboleto = self.rename_pdf()
            data = self.get_val_doc_and_codebar(nameboleto)
            self.append_success(data)

        except Exception as e:
            raise ExecutionError(e=e) from e

    def get_site(self) -> None:
        """Access the emission site.

        Navigates to the Caixa deposit page and handles CAPTCHA and
        navigation by interacting with the webpage elements. Ensures
        that subsequent deposit steps can proceed.
        """
        self.message = "Acessando página de emissão"
        self.type_log = "log"
        self.prt()

        self.driver.get("https://depositojudicial.caixa.gov.br/sigsj_internet/depositos-judiciais/justica-estadual/")
        list_opt: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'select[id="j_id5:filtroView:j_id6:tpDeposito"]')),
        )
        list_options = list_opt.find_elements(By.TAG_NAME, "option")

        for option in list_options:
            if option.text == "Depósitos Judiciais da Justiça Estadual":
                option.click()
                break

        captchainput: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'input[id="autoCaptcha"')),
        )
        val_captcha = captchainput.get_attribute("value")

        inputcaptcha: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[id="j_id5:filtroView:j_id6:j_id17:captchaView:cpatchaTextBox"]'),
            ),
        )
        inputcaptcha.send_keys(val_captcha.replace(",", ""))

        next_btn = self.driver.find_element(By.CSS_SELECTOR, 'input[class="hand btnConfirmar"]')
        next_btn.click()

        sleep(2)
        next_btn: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[id="j_id5:filtroView:mensagemView:j_id77:btnProsseguir'),
            ),
        )
        next_btn.click()

    def locale_proc(self) -> None:
        """Configure the tribunal locale.

        Selects tribunal, comarca, vara, and agency from the provided
        options. Uses the bot_data attributes to match each selection
        against the user-provided data.
        """
        self.interact.wait_caixa()

        self.message = "Informando tribunal"
        self.type_log = "log"
        self.prt()

        lista_tribunal: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'select[id="j_id5:filtroView:formFormulario:coTribunal"]'),
            ),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_tribunal:
            item: WebElement = item
            if str(self.bot_data.get("TRIBUNAL")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()

        self.message = "Informando comarca"
        self.type_log = "log"
        self.prt()

        lista_comarca: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'select[id="j_id5:filtroView:formFormulario:coComarca"]')),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_comarca:
            item: WebElement = item
            if str(self.bot_data.get("COMARCA")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()
        self.message = "Informando vara"
        self.type_log = "log"
        self.prt()
        lista_vara: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'select[id="j_id5:filtroView:formFormulario:coVara"]')),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_vara:
            item: WebElement = item
            if str(self.bot_data.get("VARA")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()
        self.message = "Informando agencia"
        self.type_log = "log"
        self.prt()
        lista_agencia: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'select[id="j_id5:filtroView:formFormulario:coAgencia"]')),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_agencia:
            item: WebElement = item
            if str(self.bot_data.get("AGENCIA")).lower() in item.text.lower():
                item.click()
                break

    def proc_nattribut(self) -> None:
        """Process the nature of the tributary.

        Inserts the process number, action type, and a default nature
        of action for the deposit. This step ensures the system
        recognizes the deposit context.
        """
        numprocess = self.bot_data.get("NUMERO_PROCESSO").split(".")
        numproc_formated = f"{numprocess[0]}.{numprocess[1]}.{numprocess[3]}.{numprocess[4]}"

        self.interact.wait_caixa()
        self.message = "Informando numero do processo"
        self.type_log = "log"
        self.prt()
        num_process: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[id="j_id5:filtroView:formFormulario:nuProcessoCNJ"]'),
            ),
        )
        num_process.send_keys(numproc_formated)

        self.interact.wait_caixa()
        self.message = "Informando tipo da ação do processo"
        self.type_log = "log"
        self.prt()
        list_type_acao_process = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:idOrigemAcao"]',
        ).find_elements(By.TAG_NAME, "option")
        for item in list_type_acao_process:
            item: WebElement = item
            if str(self.bot_data.get("TIPO_ACAO")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()
        self.message = "Informando natureza tributaria"
        self.type_log = "log"
        self.prt()
        natureza_tributaria = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:naturezaAcao"]',
        ).find_elements(By.TAG_NAME, "option")[2]
        natureza_tributaria.click()

    def dados_partes(self) -> None:
        """Input party (author/defendant) data.

        Fills in author and defendant details, including name and
        document (CPF/CNPJ). Chooses the document type automatically
        by the count_doc utility.
        """
        self.interact.wait_caixa()
        self.message = "Informando nome do autor"
        self.type_log = "log"
        self.prt()
        campo_nome_autor = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:nomeAutor"]',
        )
        campo_nome_autor.send_keys(self.bot_data.get("AUTOR"))

        self.interact.wait_caixa()
        self.message = "Informando tipo de documento do autor"
        self.type_log = "log"
        self.prt()
        doct_type = self.count_doc(self.bot_data.get("CPF_CNPJ_AUTOR"))

        if not doct_type:
            return

        doctype_autor = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:tipoDocAutor"]',
        ).find_elements(By.TAG_NAME, "option")

        for item in doctype_autor:
            item: WebElement = item
            if item.text.lower() == doct_type.lower():
                item.click()
                break

        self.interact.wait_caixa()
        self.message = "Informando documento do autor"
        self.type_log = "log"
        self.prt()

        self.interact.wait_caixa()
        campo_doc_autor = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:codDocAutor"]',
        )
        doc_autor = str(self.bot_data.get("CPF_CNPJ_AUTOR")).replace("-", "").replace(".", "").replace("/", "")
        campo_doc_autor.send_keys(doc_autor)

        self.interact.wait_caixa()
        self.meesage = "Informando réu"
        self.type_log = "log"
        self.prt()
        campo_nome_reu = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:nomeReu"]',
        )

        contraria = None
        for passivo in ["réu", "reu"]:
            contraria = self.bot_data.get(passivo.upper(), None)
            if contraria is not None:
                break

        campo_nome_reu.send_keys(self.bot_data.get("REU", contraria))

        doct_type = self.count_doc(self.bot_data.get("CPF_CNPJ_REU"))

        self.interact.wait_caixa()
        doctype_reu = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:tipoDocReu"]',
        ).find_elements(By.TAG_NAME, "option")
        for item in doctype_reu:
            if item.text.lower() == doct_type.lower():
                item.click()
                break

        self.interact.wait_caixa()
        self.message = "Informando tipo de documento réu"
        self.type_log = "log"
        self.prt()
        campo_doc_reu = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:codDocReu"]',
        )
        doc_reu = str(self.bot_data.get("CPF_CNPJ_REU")).replace(".", "").replace("-", "").replace("/", "")
        campo_doc_reu.send_keys(doc_reu)

    def info_deposito(self) -> None:
        """Provide deposit information.

        Fills in the depositor indicator (e.g., 'Réu') and the deposit
        value. Formats the deposit value to match the system’s input
        convention.
        """
        self.interact.wait_caixa()
        self.message = "Informando indicador depositante"
        self.type_log = "log"
        self.prt()
        indicador_depositante = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:idDepositante"]',
        ).find_elements(By.TAG_NAME, "option")

        for item in indicador_depositante:
            if item.text.lower() == "réu":
                item.click()
                break

        self.interact.wait_caixa()
        self.message = "Informando valor do depósito"
        self.type_log = "log"
        self.prt()
        campo_val_deposito = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:valorDeposito"]',
        )

        val_deposito = str(self.bot_data.get("VALOR_CALCULADO"))

        if "," not in val_deposito:
            val_deposito = f"{val_deposito},00"
        campo_val_deposito.send_keys(val_deposito)

    def make_doc(self) -> None:
        """Generate and download the deposit document.

        Initiates the document generation process and triggers
        the PDF download, to be renamed and processed later.
        """
        self.interact.wait_caixa()
        self.message = "Gerando documento"
        self.type_log = "log"
        self.prt()
        make_id = self.driver.find_element(By.CSS_SELECTOR, 'input[id="j_id5:filtroView:formFormulario:j_id248"]')
        make_id.click()

        self.interact.wait_caixa()
        self.message = "Baixando documento"
        self.type_log = "log"
        self.prt()
        download_pdf = self.driver.find_element(By.CSS_SELECTOR, 'a[id="j_id5:filtroView:formFormulario:j_id554"]')
        download_pdf.click()

    def rename_pdf(self) -> str:
        """Rename the downloaded PDF document.

        Uses stored bot_data attributes to format the PDF filename.
        Moves the file from a temporary path to its final location.

        Returns:
            str: The newly generated name of the PDF.

        """
        pgto_name = self.bot_data.get("NOME_CUSTOM", "Guia De Depósito")

        numproc = self.bot_data.get("NUMERO_PROCESSO")
        pdf_name = f"{pgto_name} - {numproc} - {self.bot_data.get('AUTOR')} - {self.pid}.pdf"
        sleep(3)

        caminho_old_pdf = os.path.join(self.output_dir_path, "guia_boleto.pdf")
        renamepdf = os.path.join(self.output_dir_path, pdf_name)

        sleep(1)
        shutil.move(caminho_old_pdf, renamepdf)

        return pdf_name

    def get_val_doc_and_codebar(self, pdf_name: str) -> None:
        """Extract values and barcode from the PDF document.

        Parses the generated PDF to retrieve deposit information such
        as barcodes and deposit values. Process number and other data
        are assembled into a list returned at the end.

        Args:
            pdf_name (str): The name of the PDF to parse.

        Returns:
            list: Process details, including barcodes, deposit values,
            and other metadata needed for further processing.

        """
        sleep(0.5)

        path_pdf = os.path.join(self.output_dir_path, pdf_name)
        # Inicialize uma lista para armazenar os números encontrados
        bar_code = ""
        numeros_encontrados = []

        # Expressão regular para encontrar números nesse formato
        pattern = r"\b\d{5}\.\d{5}\s*\d{5}\.\d{6}\s*\d{5}\.\d{6}\s*\d\s*\d{14}\b"

        pdf_file = path_pdf
        read = PdfReader(pdf_file)

        for page in read.pages:
            text = page.extract_text()

            with suppress(Exception):
                # Use a expressão regular para encontrar números
                numeros = re.findall(pattern, text)

                # Adicione os números encontrados à lista
                numeros_encontrados.extend(numeros)

        # Imprima os números encontrados
        for numero in numeros_encontrados:
            numero = str(numero)
            bar_code = numero.replace("  ", "").replace(" ", "").replace(".", " ")

        return [
            self.bot_data.get("NUMERO_PROCESSO"),
            self.bot_data.get("TEXTO_DESC", ""),
            self.bot_data.get("VALOR_CALCULADO"),
            self.bot_data.get("DATA_PGTO", ""),
            "condenação",
            "JEC",
            self.bot_data.get("VIA_CONDENACAO", ""),
            bar_code,
            pdf_name,
        ]
