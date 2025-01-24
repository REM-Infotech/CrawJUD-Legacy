import os
import re
import shutil
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any

from pypdf import PdfReader
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from ...common import ErroDeExecucao
from ...core import CrawJUD
from ...shared import PropertiesCrawJUD


class movimentacao(PropertiesCrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        CrawJUD.setup()
        CrawJUD.auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:

        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):

            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    CrawJUD.auth_bot()

            try:
                self.queue()

            except Exception as e:

                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        super().DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                    old_message = self.message

                    CrawJUD.auth_bot()

                if old_message is None:
                    old_message = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{
                    message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:

        try:
            self.appends = []
            self.another_append: list[tuple[Any, str, str]] = []
            self.resultados = []

            self.table_moves = None

            list_botdata = list(self.bot_data.items())
            for key, value in list_botdata:
                if value is None:
                    self.bot_data.pop(key)

            search = self.SearchBot()

            if search is not True:
                raise ErroDeExecucao(message="Processo não encontrado!")

            self.message = "Buscando movimentações"
            self.type_log = "log"
            self.prt()

            self.setup_config()

            if len(self.appends) > 0:
                self.type_log = "log"
                self.append_success(self.appends)

            if len(self.another_append) > 0:

                for data, msg, fileN in self.another_append:
                    self.append_success([data], msg, fileN)

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def set_page_size(self) -> None:

        select = Select(
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.select_page_size)
                )
            )
        )
        select.select_by_value("1000")

    def setup_config(self) -> None:

        encontrado = False
        keywords = []
        self.set_page_size()
        self.set_tablemoves()

        keyword = self.bot_data.get(
            "PALAVRA_CHAVE", self.bot_data.get("PALAVRAS_CHAVE", "*")
        )

        if keyword != "*":

            keywords.extend(keyword.split(",") if "," in keyword else [keyword])

        if len(keywords) > 0:
            for keyword in keywords:
                encontrado = self.scrap_moves(keyword)

        elif len(keywords) == 0 and keyword == "*":
            encontrado = self.scrap_moves(keyword)

        if encontrado is False:
            raise ErroDeExecucao("Nenhuma movimentação encontrada")

    def filter_moves(self, move: WebElement) -> bool:

        keyword = self.kword
        itensmove = move.find_elements(By.TAG_NAME, "td")

        if len(itensmove) < 5:
            return False

        text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")

        def data_check(data_mov: str) -> bool:
            """
            ### (function): data_check

            Por Padrão, ele utilizará a data da movimentação
            Caso o Usuario opte por filtrar por datas, ele deve
            informar a coluna `DATA_INICIO`, `DATA_FIM` ou ambas

            Args:
                data_mov (str): Data da movimentação

            Returns:
                bool: Resultado do filtro (False | True)
            """
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

            return all(
                [
                    data_mov >= data_inicio,
                    data_mov <= data_fim,
                ]
            )

        def text_check(text_mov: str) -> bool:
            """text_check `Verificação de palavra chave`

            Filtro de movimentações por palavra chave

            Args:
                text_mov (str): Texto da movimentação

            Returns:
                bool: Resultado (False | True)
            """
            check_palavra = any(
                chk is True
                for chk in [
                    keyword == "*",
                    keyword.lower() == text_mov.split("\n")[0].lower(),
                    keyword.lower() == text_mov.lower(),
                    keyword.lower() in text_mov.lower(),
                    self.similaridade(keyword.lower(), text_mov.split("\n")[0].lower())
                    > 0.8,
                ]
            )

            return check_palavra

        def check_intimado() -> bool:
            """check_intimado

            Filtro de Intimado. Eficiente para casos onde o usuário
            quer apenas movimentações em seu nome ou nome de seu cliente.

            Por Padrão, o intimado deve vir vazio para trazer todos independente

            Returns:
                bool: Resultado (False | True)
            """
            intimado_chk = True
            intimado = self.bot_data.get("INTIMADO", None)

            if intimado is not None:
                intimado_chk = str(intimado).lower() in text_mov.lower()

            return intimado_chk

        resultados = all([data_check(data_mov), text_check(text_mov), check_intimado()])

        return resultados

    def scrap_moves(self, keyword: str):

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
            message_.append(
                f'\nDATA_INICIO: <span class="fw-bold">{data_inicio}</span>'
            )
        if data_fim:
            message_.append(f'\nDATA_FIM: <span class="fw-bold">{data_fim}</span>')

        args = list(self.bot_data.items())
        pos = 0
        for pos, row in enumerate(args):
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

        def check_others(text_mov: str):

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

        """ Iteração dentro das movimentações filtradas """
        for move in move_filter:

            mov_texdoc = ""
            itensmove = move.find_elements(By.TAG_NAME, "td")

            text_mov = str(itensmove[3].text)
            data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")

            """ Outros Checks """
            mov_chk, trazerteor, mov_name, use_gpt, save_another_file = check_others(
                text_mov
            )

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

    def getAnotherMoveWithDoc(self, keyword: str):

        def getmovewithdoc(move: WebElement):

            def check_namemov(move: WebElement) -> bool:

                itensmove = move.find_elements(By.TAG_NAME, "td")
                text_mov = itensmove[3].find_element(By.TAG_NAME, "b").text
                return keyword.upper() == text_mov.upper()

            return check_namemov(move)

        return list(filter(getmovewithdoc, self.table_moves))

    def movecontainsdoc(self, move: WebElement) -> bool:

        expand = None
        with suppress(NoSuchElementException):
            self.expand_btn = move.find_element(
                By.CSS_SELECTOR, self.elements.expand_btn_projudi
            )

            expand = self.expand_btn

        return expand is not None

    def getdocmove(self, move: WebElement, save_in_anotherfile: bool = False) -> str:

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

        table_docs: WebElement = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_tr))
        )
        style_expand = table_docs.get_attribute("style")

        if style_expand == "display: none;":

            expand.click()
            while table_docs.get_attribute("style") == "display: none;":
                sleep(0.25)

            table_docs: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_tr))
            )

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
            name_pdf = self.format_String(str(link_doc.text))
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

                elif old_pdf.exists():
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
                    f"Informações da movimentação '{nome_mov}'(Proc Nº{self.bot_data.get("NUMERO_PROCESSO")})",
                    " foram salvos em uma planilha separada",
                )

                self.another_append.append(
                    (
                        data,
                        "".join(msg),
                        f"{self.pid} - Info_Mov_Docs.xlsx",
                    )
                )

            if pos == 0:
                text_doc_1 = text_mov

        return text_doc_1

    def openfile(self, path_pdf: str) -> str:

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

        table_moves = self.driver.find_element(By.CLASS_NAME, "resultTable")
        self.table_moves = table_moves.find_elements(
            By.XPATH,
            self.elements.table_moves,
        )
