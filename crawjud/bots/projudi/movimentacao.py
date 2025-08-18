"""Module: movimentacao.

Handle movement-related operations in the Projudi system with data scraping and reporting.
"""

from __future__ import annotations

import re
import shutil
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import requests
from pypdf import PdfReader
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from crawjud.bots.projudi.resources import elements as el
from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.interfaces.controllers.bots.systems.projudi import ProjudiBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


@shared_task(name="projudi.movimentacao", bind=True, base=ContextTask)
@wrap_cls
class Movimentacao(ProjudiBot):
    """Manage movements in Projudi by scraping, filtering, and logging process-related actions.

    This class extends CrawJUD to handle operations including movement search,
    keyword filtering, and report generation for movement activities.
    """

    def execution(self) -> None:
        """Loop through data rows and process each movement with error management.

        Iterates over data frame entries and queues movement processing.
        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except ExecutionError as e:
                old_message = None

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
        """Manage queuing of movement operations and scrape required data.

        Raises:
            ExecutionError: If processing fails during movement queue operations.

        """
        try:
            self.appends = []
            self.another_append: list[tuple[dict, str, str]] = []
            self.resultados = []

            self.table_moves = None

            list_botdata = list(self.bot_data.items())
            for key, value in list_botdata:
                if value is None:
                    self.bot_data.pop(key)

            search = self.search_bot()

            if search is not True:
                _raise_execution_error(message="Processo não encontrado!")

            self.message = "Buscando movimentações"
            self.type_log = "log"
            self.prt()

            self.setup_config()

            if len(self.appends) > 0:
                self.type_log = "log"
                self.append_success(self.appends)

            if len(self.another_append) > 0:
                for data, msg, fileN in self.another_append:  # noqa: N806
                    self.type_log = "info"
                    self.append_success([data], msg, fileN)

            elif len(self.appends) == 0 and len(self.another_append) == 0:
                self.message = "Nenhuma movimentação encontrada"
                self.type_log = "error"
                self.prt()
                data = self.bot_data
                data.update({"MOTIVO_ERRO": self.message})
                self.append_error(data)

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def set_page_size(self) -> None:
        """Set the page size of the movement table to 1000."""
        select = Select(
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.select_page_size,
                )),
            ),
        )
        select.select_by_value("1000")

    def setup_config(self) -> None:
        """Configure movement scraping by setting page size, table moves, and keywords.

        Raises:
            ExecutionError: If no movements are found in the scraping process.

        """
        encontrado = False
        keywords = []
        self.set_page_size()
        self.set_tablemoves()

        keyword = self.bot_data.get(
            "PALAVRA_CHAVE",
            self.bot_data.get("PALAVRAS_CHAVE", "*"),
        )

        if keyword != "*":
            keywords.extend(keyword.split(",") if "," in keyword else [keyword])

        if len(keywords) > 0:
            for keyword in keywords:
                encontrado = self.scrap_moves(keyword)

        elif len(keywords) == 0 and keyword == "*":
            encontrado = self.scrap_moves(keyword)

        if encontrado is False:
            raise ExecutionError(message="Nenhuma movimentação encontrada")

    def filter_moves(self, move: WebElement) -> bool:
        """Filtre elementos de movimentação conforme critérios de data e palavra-chave.

        Args:
            move (WebElement): Elemento de movimentação a ser filtrado.

        Returns:
            bool: Retorne True se a movimentação atender a todos os critérios, senão False.

        """
        # Obtenha a palavra-chave e os itens da movimentação
        keyword = self.kword
        itensmove = move.find_elements(By.TAG_NAME, "td")

        # Retorne False se não houver itens suficientes
        if len(itensmove) < 5:
            return False

        # Extraia texto e data da movimentação
        text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")

        # Verifique os critérios de data, texto e intimado usando métodos auxiliares
        return all([
            self._data_check(data_mov),
            self._text_check(text_mov, keyword),
            self._check_intimado(text_mov),
        ])

    def _data_check(self, data_mov: str) -> bool:
        """Valida a data informada conforme formatos e intervalo definidos.

        Args:
            data_mov (str): Data da movimentação em string.

        Returns:
            bool: True se a data estiver no intervalo, senão False.

        """
        patterns = [
            ("%d/%m/%Y", r"\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}\b"),
            ("%m/%d/%Y", r"\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/\d{4}\b"),
            ("%Y/%m/%d", r"\b\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])\b"),
            ("%Y/%d/%m", r"\b\d{4}/(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])\b"),
        ]

        for format_d, pattern in patterns:
            match_ = re.match(pattern, data_mov)
            if match_ is not None:
                data_mov_dt = datetime.strptime(data_mov, format_d).replace(
                    tzinfo=ZoneInfo("America/Manaus"),
                )
                break
        else:
            return False

        data_inicio = self.bot_data.get("DATA_INICIO", data_mov_dt)
        data_fim = self.bot_data.get("DATA_FIM", data_mov_dt)

        if not isinstance(data_inicio, datetime):
            for format_d, pattern in patterns:
                if re.match(pattern, str(data_inicio).replace(" ", "")):
                    data_inicio = datetime.strptime(
                        str(data_inicio).replace(" ", ""),
                        format_d,
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))
                    break

        if not isinstance(data_fim, datetime):
            for format_d, pattern in patterns:
                if re.match(pattern, str(data_fim).replace(" ", "")):
                    data_fim = datetime.strptime(
                        str(data_fim).replace(" ", ""),
                        format_d,
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))
                    break

        return data_inicio <= data_mov_dt <= data_fim

    def _text_check(self, text_mov: str, keyword: str) -> bool:
        """Verifique se o texto da movimentação atende aos critérios da palavra-chave.

        Args:
            text_mov (str): Texto da movimentação.
            keyword (str): Palavra-chave para filtragem.

        Returns:
            bool: True se atender aos critérios, senão False.

        """
        return any(
            chk is True
            for chk in [
                keyword == "*",
                keyword.lower() == text_mov.split("\n")[0].lower(),
                keyword.lower() == text_mov.lower(),
                keyword.lower() in text_mov.lower(),
                self.similaridade(
                    keyword.lower(),
                    text_mov.split("\n")[0].lower(),
                )
                > 0.8,
            ]
        )

    def _check_intimado(self, text_mov: str) -> bool:
        """Verifique se o bot foi intimado conforme dados da movimentação.

        Args:
            text_mov (str): Texto da movimentação.

        Returns:
            bool: True se intimado ou não aplicável, senão False.

        """
        intimado = self.bot_data.get("INTIMADO", None)
        if intimado is not None:
            return str(intimado).lower() in text_mov.lower()
        return True

    def scrap_moves(self, keyword: str) -> None:
        """Busque e processe movimentações que contenham a palavra-chave informada.

        Args:
            keyword (str): Palavra-chave para filtrar as movimentações.

        """
        self.kword = keyword
        move_filter = list(filter(self.filter_moves, self.table_moves))
        self._log_search_arguments(keyword)
        for move in move_filter:
            self._process_move(move, keyword)

    def _log_search_arguments(self, keyword: str) -> None:
        """Registre os argumentos utilizados na busca de movimentações.

        Args:
            keyword (str): Palavra-chave utilizada na busca.

        """
        message_ = [
            "\n====================================================\n",
            "Buscando movimentações que contenham os argumentos: ",
        ]
        data_inicio = self.bot_data.get("DATA_INICIO")
        data_fim = self.bot_data.get("DATA_FIM")
        message_.append(f'\nPALAVRA_CHAVE: <span class="fw-bold">{keyword}</span>')
        if data_inicio:
            message_.append(
                f'\nDATA_INICIO: <span class="fw-bold">{data_inicio}</span>',
            )
        if data_fim:
            message_.append(f'\nDATA_FIM: <span class="fw-bold">{data_fim}</span>')
        args = list(self.bot_data.items())
        for pos, (key, value) in enumerate(args):
            add_msg_ = f"   - {key}: {value} "
            _msg_ = add_msg_
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

    def _process_move(self, move: WebElement, keyword: str) -> None:
        """Processa uma movimentação filtrada, extraindo e salvando informações.

        Args:
            move (WebElement): Elemento de movimentação filtrado.
            keyword (str): Palavra-chave utilizada na busca.

        """
        mov_texdoc = ""
        itensmove = move.find_elements(By.TAG_NAME, "td")
        text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")
        mov_chk, trazerteor, mov_name, use_gpt, save_another_file = (
            self._check_others(text_mov)
        )
        nome_mov = str(itensmove[3].find_element(By.TAG_NAME, "b").text)
        movimentador, qualificacao_movimentador = self._format_movimentador(
            itensmove[4].text,
        )
        if trazerteor:
            mov_texdoc = self._get_mov_texdoc(
                mov_chk,
                mov_name,
                move,
                save_another_file,
            )
            if mov_texdoc and use_gpt:
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

    def _check_others(self, text_mov: str) -> tuple[bool, bool, str, bool, bool]:
        """Verifique opções adicionais para processamento da movimentação.

        Args:
            text_mov (str): Texto da movimentação.

        Returns:
            tuple: (mov_chk, trazer_teor, mov, use_gpt, save_another_file)

        """
        save_another_file = (
            str(self.bot_data.get("DOC_SEPARADO", "SIM")).upper() == "SIM"
        )
        mov = ""
        mov_chk = False
        trazer_teor = str(self.bot_data.get("TRAZER_TEOR", "NÃO")).upper() == "SIM"
        patterns = [
            r"Referente ao evento (.+?) \((\d{2}/\d{2}/\d{4})\)",
            r"\) ([A-Z\s]+) \((\d{2}/\d{2}/\d{4})\)",
        ]
        for pattern in patterns:
            match = re.match(pattern, text_mov)
            if match is not None:
                mov = str(match)
                mov_chk = True
        use_gpt = str(self.bot_data.get("USE_GPT", "NÃO").upper()) == "SIM"
        return (mov_chk, trazer_teor, mov, use_gpt, save_another_file)

    def _format_movimentador(self, movimentador: str) -> tuple[str, str]:
        """Formata o nome e a qualificação do movimentador.

        Args:
            movimentador (str): Texto do movimentador.

        Returns:
            tuple: (movimentador, qualificacao_movimentador)

        """
        if "SISTEMA PROJUDI" in movimentador:
            movimentador = movimentador.replace("  ", "")
            qualificacao_movimentador = movimentador
        elif "\n" in movimentador:
            info_movimentador = movimentador.split("\n ")
            movimentador = info_movimentador[0].replace("  ", "")
            qualificacao_movimentador = info_movimentador[1]
        else:
            qualificacao_movimentador = ""
        return movimentador, qualificacao_movimentador

    def _get_mov_texdoc(
        self,
        mov_name: str,
        move: WebElement,
        *mov_chk: bool,
        save_another_file: bool,
    ) -> str:
        """Obtenha o texto do documento da movimentação, se aplicável.

        Args:
            mov_chk (bool): Indica se há correspondência de movimento.
            mov_name (str): Nome do movimento.
            move (WebElement): Elemento da movimentação.
            save_another_file (bool): Salvar em arquivo separado.

        Returns:
            str: Texto do documento, se houver.

        """
        mov_texdoc = ""
        if mov_chk:
            move_doct = self.get_another_move(mov_name)
            for sub_mov in move_doct:
                mov_texdoc = self.getdocmove(sub_mov, save_another_file)
        elif self.movecontainsdoc(move):
            mov_texdoc = self.getdocmove(move, save_another_file)
        return mov_texdoc

    def get_another_move(self, keyword: str) -> list[WebElement]:
        """Retrieve movement entries that contain a document matching the keyword.

        Args:
            keyword (str): Document keyword to search for.

        Returns:
            list[WebElement]: List of movement elements that match.

        """

        def getmovewithdoc(move: WebElement) -> bool:
            def check_namemov(move: WebElement) -> bool:
                itensmove = move.find_elements(By.TAG_NAME, "td")
                text_mov = itensmove[3].find_element(By.TAG_NAME, "b").text
                return keyword.upper() == text_mov.upper()

            return check_namemov(move)

        return list(filter(getmovewithdoc, self.table_moves))

    def movecontainsdoc(self, move: WebElement) -> bool:
        """Determine if a movement element includes an associated document.

        Args:
            move (WebElement): The movement element to check.

        Returns:
            bool: True if the document exists; otherwise, False.

        """
        expand = None
        with suppress(NoSuchElementException):
            self.expand_btn = move.find_element(
                By.CSS_SELECTOR,
                el.expand_btn_projudi,
            )

            expand = self.expand_btn

        return expand is not None

    def getdocmove(
        self,
        move: WebElement,
        *,
        save_in_anotherfile: bool = False,
    ) -> str:
        """Extraia o texto do documento da movimentação, reduzindo a complexidade.

        Args:
            move (WebElement): Elemento da movimentação a ser processado.
            save_in_anotherfile (bool, optional): Se True, salva info em arquivo separado.

        Returns:
            str: Texto extraído do documento.

        """
        itensmove = move.find_elements(By.TAG_NAME, "td")
        _text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")
        nome_mov = str(itensmove[3].find_element(By.TAG_NAME, "b").text)
        movimentador, qualificacao_movimentador = self._format_movimentador(
            itensmove[4].text,
        )

        expand, css_tr = self._get_expand_and_css()
        table_docs = self._wait_and_expand_table(css_tr, expand)
        rows = table_docs.find_elements(By.TAG_NAME, "tr")[::-1]
        return self._process_doc_rows(
            rows,
            nome_mov,
            data_mov,
            movimentador,
            qualificacao_movimentador,
            save_in_anotherfile,
        )

    def _get_expand_and_css(self) -> tuple:
        """Obtenha o botão expandir e o seletor CSS da tabela de documentos.

        Returns:
            Tuple[WebElement, str]

        """
        expand = self.expand_btn
        expandattrib = expand.get_attribute("class")
        id_tr = expandattrib.replace("linkArquivos", "row")
        css_tr = f'tr[id="{id_tr}"]'
        return expand, css_tr

    def _wait_and_expand_table(self, css_tr: str, expand: WebElement) -> WebElement:
        """Aguarde e expanda a tabela de documentos se necessário.

        Returns:
            WebElement

        """
        table_docs = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, css_tr)),
        )
        style_expand = table_docs.get_attribute("style")
        if style_expand == "display: none;":
            expand.click()
            while table_docs.get_attribute("style") == "display: none;":
                sleep(0.25)
        sleep(2)

        return self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, css_tr)),
        )

    def _process_doc_rows(
        self,
        rows: list,
        nome_mov: str,
        data_mov: str,
        movimentador: str,
        qualificacao_movimentador: str,
        *,
        save_in_anotherfile: bool,
    ) -> str:
        """Processa as linhas de documentos, baixa e extrai texto do PDF.

        Returns:
            str

        """
        text_doc_1 = ""
        max_rows = len(rows) - 1
        for pos, docs in enumerate(rows):
            path_pdf, nomearquivo = self._prepare_pdf_path(nome_mov, pos)
            if Path(path_pdf).exists():
                continue
            self._download_or_move_pdf(docs, path_pdf)
            text_mov = self.openfile(path_pdf)
            data = {
                "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
                "Data movimentação": data_mov,
                "Nome Movimentação": nome_mov,
                "Texto da movimentação": text_mov,
                "Nome peticionante": movimentador,
                "Classiicação Peticionante": qualificacao_movimentador,
                "Nome Arquivo (Caso Tenha)": "".join(nomearquivo),
            }
            if save_in_anotherfile:
                msg = (
                    f"Informações da movimentação '{nome_mov}'(Proc Nº{self.bot_data.get('NUMERO_PROCESSO')})",
                    " foram salvos em uma planilha separada",
                )
                self.another_append.append((
                    data,
                    "".join(msg),
                    f"{self.pid} - Info_Mov_Docs.xlsx",
                ))
            if pos == max_rows:
                text_doc_1 = text_mov
        return text_doc_1

    def _prepare_pdf_path(self, nome_mov: str, pos: int) -> tuple:
        """Prepara o caminho do PDF e o nome do arquivo.

        Returns:
            tuple

        """
        numproc = self.bot_data.get("NUMERO_PROCESSO")
        nomearquivo = (
            f"{numproc}",
            f" - {nome_mov.upper()} - {self.pid} - DOC{pos}.pdf",
        )
        path_pdfs = Path(self.output_dir_path).resolve().joinpath(numproc)
        path_pdfs.mkdir(exist_ok=True, parents=True)
        path_pdf = Path(path_pdfs).joinpath("".join(nomearquivo))
        return path_pdf, nomearquivo

    def _download_or_move_pdf(self, docs: WebElement, path_pdf: Path) -> None:
        """Realiza o download do PDF ou move o arquivo baixado pelo navegador."""
        doc = docs.find_elements(By.TAG_NAME, "td")[4]
        link_doc = doc.find_element(By.TAG_NAME, "a")
        name_pdf = self.format_string(str(link_doc.text))
        _old_pdf = Path(self.output_dir_path).joinpath(name_pdf)
        url = link_doc.get_attribute("href")
        cookies = {
            cookie["name"]: cookie["value"] for cookie in self.driver.get_cookies()
        }
        response = requests.get(
            url,
            cookies=cookies,
            allow_redirects=True,
            timeout=60,
        )
        if response.status_code == 200:
            with Path(path_pdf).open("wb") as f:
                f.write(response.content)
        else:
            self._fallback_download(url, name_pdf, path_pdf)

    def _fallback_download(self, url: str, name_pdf: str, path_pdf: Path) -> None:
        """Fallback para download do PDF via navegador caso requests falhe."""
        self.driver.get(url)
        sleep(2)
        file_found = False
        while not file_found:
            for root, _, files in self.output_dir_path.walk():
                for f in files:
                    grau_similaridade = self.similaridade(name_pdf, f)
                    if grau_similaridade > 0.8:
                        old_pdf = Path(root).joinpath(f)
                        shutil.move(old_pdf, path_pdf)
                        file_found = True
                        break
                if file_found:
                    break
            if not file_found:
                sleep(0.5)

    def openfile(self, path_pdf: str) -> str:
        """Open a PDF file and extract its text content.

        Args:
            path_pdf (str): The file path of the PDF.

        Returns:
            str: The extracted text from the PDF.

        """
        with Path(path_pdf).open("rb") as pdf:
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
        """Locate the movement table and assign its elements to self.table_moves."""
        table_moves = self.driver.find_element(By.CLASS_NAME, "resultTable")
        self.table_moves = table_moves.find_elements(
            By.XPATH,
            el.table_moves,
        )
