"""Module: movimentacao.

This module manages movement operations on the Esaj system using the CrawJUD framework.
"""

from __future__ import annotations

import re
import time
from contextlib import suppress
from datetime import datetime
from time import sleep
from typing import TYPE_CHECKING, Self
from zoneinfo import ZoneInfo

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.bots.esaj.resources import elements as el
from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.interfaces.controllers.bots.systems.esaj import ESajBot

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot


class Movimentacao(ESajBot):
    """Class Movimentacao.

    Handles all movement-related tasks in the Esaj system.

    Attributes:
        start_time (float): Timestamp when movements begin processing.
        appends (list): Collection of movement records.


    Methods:
        initialize: Create a new Movimentacao instance.
        execution: Iterate over process rows and process movements.
        queue: Queue tasks for retrieving and appending movements.
        get_moves: Extract movement information from page elements.

    """

    @classmethod
    def initialize(cls, *args: str | int, **kwargs: str | int) -> Self:
        """Initialize a new Movimentacao instance.

        Args:
            *args (str | int): Variable arguments.
            **kwargs (str | int): Keyword arguments.

        Returns:
            Self: A new Movimentacao instance.

        # Inline: Directly return an instance with given arguments.

        """
        return cls(*args, **kwargs)

    def __init__(self, *args: str | int, **kwargs: str | int) -> None:
        """Construct the Movimentacao instance.

        Sets up the crawler by configuring authentication and environment.

        Args:
            *args: Positional arguments for setup.
            **kwargs: Keyword arguments for configuration.

        # Inline: Leverage parent classes for setup and authentication.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute movement processing.

        Iterates over each process row, handling session renewal and error logging.

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
                # TODO(Nicholas Silva): Criação de Exceptions
                # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando...",
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
        """Manage queuing of movement operations and scrape required data.

        Raises:
            ExecutionError: If processing fails during movement queue operations.

        """
        try:
            self.appends = []
            self.another_append: list[tuple[dict, str, str]] = []
            self.resultados = []

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

    def filter_moves(self, move: WebElementBot) -> bool:
        """Filtra um elemento de movimentação com base em critérios de data e palavra-chave.

        Args:
            move (WebElementBot): Elemento de movimentação a ser filtrado.

        Returns:
            bool: Retorna True se a movimentação atender a todos os critérios, caso contrário, False.

        """
        # Obtém a palavra-chave e os itens da movimentação
        keyword = self.kword
        itensmove = move.find_elements(By.TAG_NAME, "td")

        # Verifica se há itens suficientes para análise
        if len(itensmove) < 5:
            return False

        text_mov = str(itensmove[2].text)
        data_mov = str(itensmove[0].text.strip())

        # Aplica os filtros de data, texto e intimado
        if not self._data_check(data_mov):
            return False
        if not self._text_check(text_mov, keyword):
            return False
        return self._check_intimado(text_mov)

    def _data_check(self, data_mov: str) -> bool:
        """Valida a string de data fornecida contra múltiplos formatos e verifica se está dentro do intervalo especificado.

        Args:
            data_mov (str): String de data a ser validada.

        Returns:
            bool: True se a data for válida e estiver dentro do intervalo, False caso contrário.

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
            data_mov_dt = None

        if data_mov_dt is None:
            return False

        data_inicio = self.bot_data.get("DATA_INICIO", data_mov_dt)
        data_fim = self.bot_data.get("DATA_FIM", data_mov_dt)

        if not isinstance(data_inicio, datetime):
            for format_d, pattern in patterns:
                if re.match(pattern, str(data_inicio)):
                    data_inicio = datetime.strptime(
                        str(data_inicio).replace(" ", ""),
                        format_d,
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))
                    break

        if not isinstance(data_fim, datetime):
            for format_d, pattern in patterns:
                if re.match(pattern, str(data_fim)):
                    data_fim = datetime.strptime(
                        str(data_fim).replace(" ", ""),
                        format_d,
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))
                    break

        return all([data_mov_dt >= data_inicio, data_mov_dt <= data_fim])

    def _text_check(self, text_mov: str, keyword: str) -> bool:
        """Verifica se o texto da movimentação atende aos critérios de palavra-chave.

        Args:
            text_mov (str): Texto da movimentação.
            keyword (str): Palavra-chave para filtragem.

        Returns:
            bool: True se algum critério for atendido, False caso contrário.

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
        """Verifica se o bot foi intimado com base nos dados do bot.

        Args:
            text_mov (str): Texto da movimentação.

        Returns:
            bool: True se o bot foi intimado ou se a chave não está presente, False caso contrário.

        """
        intimado = self.bot_data.get("INTIMADO", None)
        if intimado is not None:
            return str(intimado).lower() in text_mov.lower()
        return True

    def scrap_moves(self, keyword: str) -> None:
        """Realize scraping das movimentações que contenham a palavra-chave informada.

        Args:
            keyword (str): Palavra-chave para filtrar as movimentações.

        """
        self.kword = keyword
        move_filter = list(filter(self.filter_moves, self.table_moves))
        self._log_scrap_moves_header(keyword)
        for move in move_filter:
            self._process_single_move(move, keyword)

    def _log_scrap_moves_header(self, keyword: str) -> None:
        """Gera e exibe o cabeçalho de log para a busca de movimentações.

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
        for idx, (key, value) in enumerate(args):
            add_msg_ = f"   - {key}: {value} "
            _msg_ = add_msg_
            if "\n\nArgumentos Adicionais: \n" not in message_:
                message_.append("\n\nArgumentos Adicionais: \n")
            if key not in ["TRAZER_PDF", "TRAZER_TEOR", "USE_GPT", "DOC_SEPARADO"]:
                continue
            if key not in message_:
                message_.append(f"{_msg_}\n")
            if idx + 1 == len(args):
                _msg_ += "\n====================================================\n"
                message_.append(_msg_)
        self.message = "".join(message_)
        self.type_log = "info"
        self.prt()

    def _check_others(self, text_mov: str) -> tuple[bool, bool, str, bool, bool]:
        """Realiza verificações adicionais para a movimentação.

        Args:
            text_mov (str): Texto da movimentação.

        Returns:
            tuple: Flags e informações auxiliares para processamento.

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

    def _process_single_move(self, move: WebElementBot, keyword: str) -> None:
        """Processa uma única movimentação filtrada.

        Args:
            move: Elemento de movimentação.
            keyword (str): Palavra-chave utilizada na busca.

        """
        mov_texdoc = ""
        itensmove = move.find_elements(By.TAG_NAME, "td")
        text_mov = str(itensmove[3].text)
        data_mov = str(itensmove[2].text.split(" ")[0]).replace(" ", "")
        mov_chk, trazerteor, mov_name, use_gpt, save_another_file = (
            self._check_others(
                text_mov,
            )
        )
        nome_mov = str(itensmove[3].find_element(By.TAG_NAME, "b").text)
        movimentador = itensmove[4].text
        # Formatação Nome Movimentador
        if "SISTEMA PROJUDI" in movimentador:
            movimentador = movimentador.replace("  ", "")
            qualificacao_movimentador = movimentador
        elif "\n" in movimentador:
            info_movimentador = movimentador.split("\n ")
            movimentador = info_movimentador[0].replace("  ", "")
            qualificacao_movimentador = info_movimentador[1]
        else:
            qualificacao_movimentador = ""
        # Verifica se o usuario optou por trazer o texto do documento caso seja mencionado um no andamento
        if trazerteor:
            if mov_chk:
                move_doct = self.get_another_move(mov_name)
                for sub_mov in move_doct:
                    mov_texdoc = self.getdocmove(sub_mov, save_another_file)
            elif self.movecontainsdoc(move):
                mov_texdoc = self.getdocmove(move, save_another_file)
            if mov_texdoc is not None and mov_texdoc != "" and use_gpt is True:
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

    def set_page_size(self) -> None:
        """Set the page size for movement scraping."""
        try:
            self.driver.execute_script(
                'document.querySelector("#tabelaTodasMovimentacoes").style.display = "block"',
            )

        except AttributeError:
            self.driver.execute_script(
                'document.querySelector("#tabelaUltimasMovimentacoes").style.display = "block"',
            )

    def set_tablemoves(self) -> None:
        """Set the table moves element."""
        from selenium.common.exceptions import NoSuchElementException

        try:
            table_moves = self.driver.find_element(
                By.CSS_SELECTOR,
                el.movimentacoes,
            )
        except NoSuchElementException:
            table_moves = self.driver.find_element(
                By.ID,
                el.ultimas_movimentacoes,
            )

        self.table_moves = table_moves.find_elements(
            By.XPATH,
            el.table_moves,
        )

    def get_moves(self) -> None:
        """Retrieve movement information.

        Extracts and appends movement details from the page elements.

        # Inline: Scroll to element, reveal table, then iterate through rows.
        """
        show_all = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'a[id="linkmovimentacoes"]',
            )),
        )

        self.interact.scroll_to(show_all)

        # Rolar até o elemento
        self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all)

        # Use JavaScript para clicar no elemento
        self.driver.execute_script("arguments[0].click();", show_all)

        sleep(0.5)

        try:
            table_moves = self.driver.find_element(
                By.CSS_SELECTOR,
                el.movimentacoes,
            )
            self.driver.execute_script(
                'document.querySelector("#tabelaTodasMovimentacoes").style.display = "block"',
            )

        except NoSuchElementException:
            table_moves = self.driver.find_element(
                By.ID,
                el.ultimas_movimentacoes,
            )
            self.driver.execute_script(
                'document.querySelector("#tabelaUltimasMovimentacoes").style.display = "block"',
            )

        itens = table_moves.find_elements(By.TAG_NAME, "tr")

        palavra_chave = str(self.bot_data.get("PALAVRA_CHAVE"))
        termos = [palavra_chave]

        if "," in palavra_chave:
            termos = palavra_chave.replace(", ", ",").split(",")

        for termo in termos:
            self.message = f'Buscando movimentações que contenham "{termo}"'
            self.type_log = "log"

            for item in itens:
                td_tr = item.find_elements(By.TAG_NAME, "td")
                mov = td_tr[2].text

                if termo.lower() in mov.lower():
                    data_mov = td_tr[0].text

                    with suppress(Exception):
                        if type(data_mov) is str:
                            data_mov = datetime.strptime(
                                data_mov.replace("/", "-"),
                                "%d-%m-%Y",
                            ).replace(tzinfo=ZoneInfo("America/Manaus"))

                    name_mov = mov.split("\n")[0]
                    text_mov = td_tr[2].find_element(By.TAG_NAME, "span").text
                    self.appends.append([
                        self.bot_data.get("NUMERO_PROCESSO"),
                        data_mov,
                        name_mov,
                        text_mov,
                        "",
                        "",
                    ])
