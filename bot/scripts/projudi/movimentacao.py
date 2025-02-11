"""Module: movimentacao.

This module handles movement-related operations within the Projudi system of the CrawJUD-Bots application.
"""

import os
import re
import shutil
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep

# from typing import any
from pypdf import PdfReader
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from ...common import ExecutionError
from ...core import CrawJUD

# from ...shared import PropertiesCrawJUD


class Movimentacao(CrawJUD):
    """Handles movement-related operations within the Projudi system.

    Inherits from CrawJUD.

    Attributes:
        start_time (float): The start time of execution.

    """

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize the movimentacao instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        super().__init__()
        # PropertiesCrawJUD.kwargs = kwargs
        # for key, value in list(kwargs.items()):
        #     setattr(PropertiesCrawJUD, key, value)

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the movement processing.

        Processes each row in the data frame and handles queueing and error management.
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
                # windows = self.driver.window_handles

                # if len(windows) == 0:
                #     with suppress(Exception):
                #         self.DriverLaunch(message="Webdriver encerrado inesperadamente, reinicializando...")

                #     old_message = self.message

                #     self.auth_bot()

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
        """Manage the queuing of movement operations.

        Raises:
            ExecutionError: If the process is not found or other execution errors occur.

        """
        try:
            self.appends = []
            self.another_append: list[tuple[any, str, str]] = []
            self.resultados = []

            self.table_moves = None

            list_botdata = list(self.bot_data.items())
            for key, value in list_botdata:
                if value is None:
                    self.bot_data.pop(key)

            search = self.search_bot()

            if search is not True:
                raise ExecutionError(message="Processo não encontrado!")

            self.message = "Buscando movimentações"
            self.type_log = "log"
            self.prt()

            self.setup_config()

            if len(self.appends) > 0:
                self.type_log = "log"
                self.append_success(self.appends)

            if len(self.another_append) > 0:
                for data, msg, fileN in self.another_append:  # noqa: N806
                    self.append_success([data], msg, fileN)

            elif len(self.appends) == 0 and len(self.another_append) == 0:
                self.message = "Nenhuma movimentação encontrada"
                self.type_log = "error"
                self.prt()
                data = self.bot_data
                data.update({"MOTIVO_ERRO": self.message})
                self.append_error(data)

        except Exception as e:
            raise ExecutionError(e=e) from e

    def set_page_size(self) -> None:
        """Set the page size for the movement table.

        Selects the value '1000' from the page size dropdown.
        """
        select = Select(
            self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.select_page_size))),
        )
        select.select_by_value("1000")

    def setup_config(self) -> None:
        """Configure the setup for movement scraping.

        Sets the page size, table moves, and initiates the scraping based on keywords.

        Raises:
            ExecutionError: If no movements are found.

        """
        encontrado = False
        keywords = []
        self.set_page_size()
        self.set_tablemoves()

        keyword = self.bot_data.get("PALAVRA_CHAVE", self.bot_data.get("PALAVRAS_CHAVE", "*"))

        if keyword != "*":
            keywords.extend(keyword.split(",") if "," in keyword else [keyword])

        if len(keywords) > 0:
            for keyword in keywords:
                encontrado = self.scrap_moves(keyword)

        elif len(keywords) == 0 and keyword == "*":
            encontrado = self.scrap_moves(keyword)

        if encontrado is False:
            raise ExecutionError("Nenhuma movimentação encontrada")

    def filter_moves(self, move: WebElement) -> bool:  # noqa: C901
        """Filter movements based on date and keyword criteria.

        Args:
            move (WebElement): The movement element to filter.

        Returns:
            bool: True if the movement meets all filtering criteria, False otherwise.

        """
        keyword = self.kword
        itensmove = move.find_elements(By.TAG_NAME, "td")

        if len(itensmove) < 5:
            return False

        text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")

        def data_check(data_mov: str) -> bool:
            """Validate the given date string against multiple date formats and checks if it falls within a specified date range.

            Args:
                data_mov (str): The date string to be validated.

            Returns:
                bool: True if the date string is valid and falls within the specified date range, False otherwise.
            The function performs the following steps:
            1. Tries to match the given date string against multiple date formats.
            2. Converts the matched date string to a datetime object.
            3. Retrieves the start and end dates from the bot's data.
            4. Validates and converts the start and end dates if they are not already datetime objects.
            5. Checks if the given date falls within the start and end dates.
            The supported date formats are:
            - "%d/%m/%Y"
            - "%m/%d/%Y"
            - "%Y/%m/%d"
            - "%Y/%d/%m"

            """  # noqa: E501
            patterns = [
                ("%d/%m/%Y", r"\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}\b"),
                ("%m/%d/%Y", r"\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/\d{4}\b"),
                ("%Y/%m/%d", r"\b\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])\b"),
                ("%Y/%d/%m", r"\b\d{4}/(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])\b"),
            ]

            for format_d, pattern in patterns:
                match_ = re.match(pattern, data_mov)
                match_: re.Match | None = match_
                if match_ is not None:
                    data_mov = datetime.strptime(data_mov, format_d)
                    break

            data_inicio = self.bot_data.get("DATA_INICIO", data_mov)
            data_fim = self.bot_data.get("DATA_FIM", data_mov)
            chk_datafim = type(data_fim) is datetime
            chk_datainicio = type(data_inicio) is datetime

            if chk_datainicio is False:
                for format_d, pattern in patterns:
                    data_inicio.replace(" ", "")
                    match_ = re.match(pattern, data_mov)
                    match_: re.Match | None = match_
                    if match_ is not None:
                        data_inicio = datetime.strptime(data_inicio, format_d)
                        break

            if chk_datafim is False:
                for format_d, pattern in patterns:
                    data_fim.replace(" ", "")

                    match_ = re.match(pattern, data_mov)
                    match_: re.Match | None = match_
                    if match_ is not None:
                        data_fim = datetime.strptime(data_fim, format_d)
                        break

            return all([data_mov >= data_inicio, data_mov <= data_fim])

        def text_check(text_mov: str) -> bool:
            """Check if the given text matches certain criteria.

            This function evaluates whether the provided text (`text_mov`) meets any of the following conditions:
            - Contains a keyword that is an asterisk ("*").
            - The first line of the text matches a keyword (case-insensitive).
            - The entire text matches a keyword (case-insensitive).
            - The keyword is a substring of the text (case-insensitive).
            - The similarity between the keyword and the first line of the text is greater than 0.8.

            Args:
                text_mov (str): The text to be checked.

            Returns:
                bool: True if any of the conditions are met, False otherwise.

            """
            check_palavra = any(
                chk is True
                for chk in [
                    keyword == "*",
                    keyword.lower() == text_mov.split("\n")[0].lower(),
                    keyword.lower() == text_mov.lower(),
                    keyword.lower() in text_mov.lower(),
                    self.similaridade(keyword.lower(), text_mov.split("\n")[0].lower()) > 0.8,
                ]
            )

            return check_palavra

        def check_intimado() -> bool:
            """Check if the bot is intimated based on the bot data.

            This function checks if the bot has been intimated by looking for the
            "INTIMADO" key in the bot data. If the key is present, it verifies if
            the value associated with the key is present in the text_mov string
            (case insensitive).

            Returns:
                bool: True if the bot is intimated or if the "INTIMADO" key is not
                present in the bot data, False otherwise.

            """
            intimado_chk = True
            intimado = self.bot_data.get("INTIMADO", None)

            if intimado is not None:
                intimado_chk = str(intimado).lower() in text_mov.lower()

            return intimado_chk

        resultados = all([data_check(data_mov), text_check(text_mov), check_intimado()])

        return resultados

    def scrap_moves(self, keyword: str) -> None:  # noqa: C901
        """Scrape movements that contain the specified keyword.

        Args:
            keyword (str): The keyword to search for in movements.

        Raises:
            ExecutionError: If an error occurs during scraping.

        Returns:
            bool: True if any movements are found, False otherwise.

        """
        self.kword = keyword
        move_filter = list(filter(self.filter_moves, self.table_moves))

        message_ = [
            "\n====================================================\n",
            "Buscando movimentações que contenham os argumentos: ",
        ]

        data_inicio = self.bot_data.get("DATA_INICIO")
        data_fim = self.bot_data.get("DATA_FIM")

        message_.append(f'\nPALAVRA_CHAVE: <span class="fw-bold">{keyword}</span>')
        if data_inicio:
            message_.append(f'\nDATA_INICIO: <span class="fw-bold">{data_inicio}</span>')
        if data_fim:
            message_.append(f'\nDATA_FIM: <span class="fw-bold">{data_fim}</span>')

        args = list(self.bot_data.items())
        pos = 0
        for _, row in enumerate(args):
            key, value = row

            _add_msg = f"   - {key}: {value} "
            _msg_ = _add_msg

            if "\n\nArgumentos Adicionais: \n" not in message_:
                message_.append("\n\nArgumentos Adicionais: \n")

            if key not in ["TRAZER_PDF", "TRAZER_TEOR", "USE_GPT", "DOC_SEPARADO"]:
                continue

            if key not in message_:
                message_.append(f"{_msg_}\n")

        if pos + 1 == len(args):
            _msg_ += "\n====================================================\n"
            message_.append(_msg_)

        self.message = "".join(message_)

        self.type_log = "info"
        self.prt()

        """ Checagens dentro do Loop de movimentações """

        def check_others(text_mov: str) -> tuple[bool, bool, str, bool, bool]:
            save_another_file = str(self.bot_data.get("DOC_SEPARADO", "SIM")).upper() == "SIM"

            mov = ""
            mov_chk = False
            trazer_teor = str(self.bot_data.get("TRAZER_TEOR", "NÃO")).upper() == "SIM"

            patterns = [r"Referente ao evento (.+?) \((\d{2}/\d{2}/\d{4})\)", r"\) ([A-Z\s]+) \((\d{2}/\d{2}/\d{4})\)"]
            for pattern in patterns:
                match = re.match(pattern, text_mov)

                if match is not None:
                    mov = str(match)
                    mov_chk = True

            use_gpt = str(self.bot_data.get("USE_GPT", "NÃO").upper()) == "SIM"

            return (mov_chk, trazer_teor, mov, use_gpt, save_another_file)

        """ Iteração dentro das movimentações filtradas """
        for move in move_filter:
            mov_texdoc = ""
            itensmove = move.find_elements(By.TAG_NAME, "td")

            text_mov = str(itensmove[3].text)
            data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")

            """ Outros Checks """
            mov_chk, trazerteor, mov_name, use_gpt, save_another_file = check_others(text_mov)

            nome_mov = str(itensmove[3].find_element(By.TAG_NAME, "b").text)
            movimentador = itensmove[4].text

            """ Formatação Nome Movimentador """
            if "SISTEMA PROJUDI" in movimentador:
                movimentador = movimentador.replace("  ", "")
                qualificacao_movimentador = movimentador

            elif "\n" in movimentador:
                info_movimentador = movimentador.split("\n ")
                movimentador = info_movimentador[0].replace("  ", "")
                qualificacao_movimentador = info_movimentador[1]

            """ Verifica se o usuario optou por trazer o texto do documento caso seja mencionado um no andamento """
            if trazerteor:
                if mov_chk:
                    move_doct = self.getAnotherMoveWithDoc(mov_name)
                    for sub_mov in move_doct:
                        mov_texdoc = self.getdocmove(sub_mov, save_another_file)

                elif self.movecontainsdoc(move):
                    mov_texdoc = self.getdocmove(move, save_another_file)

                if mov_texdoc is not None and mov_texdoc != "":
                    if use_gpt is True:
                        mov_texdoc = self.gpt_chat(mov_texdoc)

            data = {
                "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
                "Data movimentação": data_mov,
                "Nome Movimentação": nome_mov,
                "Texto da movimentação": text_mov,
                "Nome peticionante": movimentador,
                "Classiicação Peticionante": qualificacao_movimentador,
                "Texto documento Mencionado (Caso Tenha)": mov_texdoc,
            }
            ms_ = [f'Movimentação "{nome_mov}" salva na planilha!']
            if keyword != "*":
                ms_.append(f" Parâmetro: {keyword}")
            self.message = "".join(ms_)

            self.type_log = "info"
            self.prt()

            self.appends.append(data)

    def getAnotherMoveWithDoc(self, keyword: str) -> list[WebElement]:  # noqa: N802
        """Retrieve another move with the specified document keyword.

        Args:
            keyword (str): The keyword to search for in moves.

        Returns:
            list: A list of moves that match the keyword.

        """

        def getmovewithdoc(move: WebElement) -> bool:
            def check_namemov(move: WebElement) -> bool:
                itensmove = move.find_elements(By.TAG_NAME, "td")
                text_mov = itensmove[3].find_element(By.TAG_NAME, "b").text
                return keyword.upper() == text_mov.upper()

            return check_namemov(move)

        return list(filter(getmovewithdoc, self.table_moves))

    def movecontainsdoc(self, move: WebElement) -> bool:
        """Check if a movement contains a document.

        Args:
            move (WebElement): The movement element to check.

        Returns:
            bool: True if the movement contains a document, False otherwise.

        """
        expand = None
        with suppress(NoSuchElementException):
            self.expand_btn = move.find_element(By.CSS_SELECTOR, self.elements.expand_btn_projudi)

            expand = self.expand_btn

        return expand is not None

    def getdocmove(self, move: WebElement, save_in_anotherfile: bool = None) -> str:  # noqa: C901, FBT001
        """Retrieve the document associated with a movement.

        Args:
            move (WebElement): The movement element.
            save_in_anotherfile (bool, optional): Whether to save the document in another file. Defaults to False.

        Returns:
            str: The text content of the document.

        """
        itensmove = move.find_elements(By.TAG_NAME, "td")

        text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")

        nome_mov = str(itensmove[3].find_element(By.TAG_NAME, "b").text)
        movimentador = itensmove[4].text

        """ Formatação Nome Movimentador """
        if "SISTEMA PROJUDI" in movimentador:
            movimentador = movimentador.replace("  ", "")
            qualificacao_movimentador = movimentador

        elif "\n" in movimentador:
            info_movimentador = movimentador.split("\n ")
            movimentador = info_movimentador[0].replace("  ", "")
            qualificacao_movimentador = info_movimentador[1]

        """ Botão para ver os documentos da movimentação """
        expand = self.expand_btn
        expandattrib = expand.get_attribute("class")
        id_tr = expandattrib.replace("linkArquivos", "row")
        css_tr = f'tr[id="{id_tr}"]'

        table_docs: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, css_tr)))
        style_expand = table_docs.get_attribute("style")

        if style_expand == "display: none;":
            expand.click()
            while table_docs.get_attribute("style") == "display: none;":
                sleep(0.25)

            table_docs: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, css_tr)))

        text_doc_1 = ""

        rows = table_docs.find_elements(By.TAG_NAME, "tr")
        for pos, docs in enumerate(rows):
            nomearquivo = (
                f"{self.bot_data.get('NUMERO_PROCESSO')}",
                f" - {nome_mov.upper()} - {self.pid} - DOC{pos}.pdf",
            )
            path_pdf = os.path.join(self.output_dir_path, "".join(nomearquivo))

            if os.path.exists(path_pdf):
                continue

            doc = docs.find_elements(By.TAG_NAME, "td")[4]
            link_doc = doc.find_element(By.TAG_NAME, "a")
            name_pdf = self.format_string(str(link_doc.text))
            old_pdf = Path(os.path.join(self.output_dir_path), name_pdf)
            url = link_doc.get_attribute("href")

            self.driver.get(url)
            while True:
                recent_folder = self.get_recent(self.output_dir_path)
                file_recent = ""

                if recent_folder is not None:
                    file_recent = os.path.basename(recent_folder)

                grau_similaridade = self.similaridade(name_pdf, file_recent)

                if grau_similaridade > 0.8:
                    old_pdf = recent_folder

                    if Path(old_pdf).exists() is False:
                        continue

                    break

                if old_pdf.exists():
                    old_pdf = str(old_pdf)
                    break

                sleep(0.5)

            shutil.move(old_pdf, path_pdf)

            text_mov = self.openfile(path_pdf)

            if str(self.bot_data.get("TRAZER_PDF", "NÃO")).upper() == "NÃO":
                sleep(1)
                Path(path_pdf).unlink(missing_ok=True)

            data = {
                "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
                "Data movimentação": data_mov,
                "Nome Movimentação": nome_mov,
                "Texto da movimentação": text_mov,
                "Nome peticionante": movimentador,
                "Classiicação Peticionante": qualificacao_movimentador,
                "Nome Arquivo (Caso Tenha)": "".join(nomearquivo),
            }
            if save_in_anotherfile is True:
                msg = (
                    f"Informações da movimentação '{nome_mov}'(Proc Nº{self.bot_data.get('NUMERO_PROCESSO')})",
                    " foram salvos em uma planilha separada",
                )

                self.another_append.append((data, "".join(msg), f"{self.pid} - Info_Mov_Docs.xlsx"))

            if pos == 0:
                text_doc_1 = text_mov

        return text_doc_1

    def openfile(self, path_pdf: str) -> str:
        """Open and reads the content of a PDF file.

        Args:
            path_pdf (str): The path to the PDF file.

        Returns:
            str: The extracted text content from the PDF.

        """
        with open(path_pdf, "rb") as pdf:
            read = PdfReader(pdf)
            # Read PDF
            pagescontent = ""
            for page in read.pages:
                with suppress(Exception):
                    text = page.extract_text()
                    remove_n_space = text.replace("\n", " ")
                    pagescontent = pagescontent + remove_n_space

        return pagescontent

    def set_tablemoves(self) -> None:
        """Set the table of movements from the web driver.

        Locates and assigns the movement table elements to the instance.
        """
        table_moves = self.driver.find_element(By.CLASS_NAME, "resultTable")
        self.table_moves = table_moves.find_elements(By.XPATH, self.elements.table_moves)
