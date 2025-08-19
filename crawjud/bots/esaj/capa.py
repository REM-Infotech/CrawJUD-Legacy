"""Manage capa operations and extract process information for CrawJUD-Bots.

This module executes the workflow to search and process process details,
ensuring detailed extraction and logging of information.
"""

from __future__ import annotations

import time
from contextlib import suppress
from typing import TYPE_CHECKING, Self

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.esaj import ESajBot
from crawjud.resources.elements import esaj as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot


class Capa(ESajBot):
    """Perform capa tasks by searching and extracting process details robustly.

    This class handles process information retrieval including form extraction
    and logging. It supports multiple process degrees.
    """

    @classmethod
    def initialize(cls, *args: str | int, **kwargs: str | int) -> Self:
        """Initialize a Capa instance with given parameters and settings.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Returns:
            Self: A new instance of Capa.

        """
        return cls(*args, **kwargs)

    def __init__(self, *args: str | int, **kwargs: str | int) -> None:
        """Initialize Capa instance and authenticate the bot for processing.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Side Effects:
            Authenticates the bot and records the start time.

        """
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute capa processing by iterating over rows with robust error handling.

        Iterates over the dataframe, renews sessions when expired, and logs errors
        for each process.
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
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando...",
                        )

                    self.auth_bot()

                message_error = str(e)

                self.print_msg(message=f"{message_error}.", type_log="error")

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Queue capa tasks by searching for process data and appending details to logs.

        Calls the search method and retrieves detailed process information.

        Raises:
            ExecutionError: Erro de execução

        """
        try:
            search = self.search_bot()

            if search is False:
                _raise_execution_error(message="Processo não encontrado.")

            self.append_success(self.get_process_informations())

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(e=e) from e

    def get_process_informations(self) -> list:
        """Extraia informações detalhadas do processo a partir dos elementos web.

        Args:
            Nenhum.

        Returns:
            list: Lista estruturada contendo detalhes do processo como área, fórum e valor.

        Raises:
            Nenhuma exceção específica.

        """
        # Log de início da extração
        self.message = f"Extraindo informações do processo nº{self.bot_data.get('NUMERO_PROCESSO')}"
        self.type_log = "log"
        self.prt()

        _grau = self._parse_grau(self.bot_data.get("GRAU", 1))
        self.driver.execute_script("$('div#maisDetalhes').show()")

        data = {"NUMERO_PROCESSO": ""}
        self._extract_sumary_information(data)
        self._extract_partes_information(data)

        return [data]

    def _parse_grau(self, grau: int | str) -> int:
        """Parse o grau do processo para inteiro.

        Args:
            grau (int|str): Grau do processo.

        Returns:
            int: Grau convertido para inteiro.

        """
        if not grau:
            return 1
        if isinstance(grau, str):
            if "º" in grau:
                grau = grau.replace("º", "")
            return int(grau)
        return grau

    def _extract_sumary_information(self, data: dict) -> None:
        """Extraia informações do sumário e atualize o dicionário de dados.

        Args:
            data (dict): Dicionário a ser atualizado com informações do sumário.

        """
        sumary_1_esaj = self.wait.until(
            ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, el.sumary_header_1),
            ),
        )
        sumary_2_esaj = self.wait.until(
            ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, el.sumary_header_2),
            ),
        )
        list_sumary = [sumary_1_esaj, sumary_2_esaj]

        for pos_, sumary in enumerate(list_sumary):
            for pos, rows in enumerate(sumary):
                subitems_sumary = rows.find_elements(
                    By.CSS_SELECTOR,
                    el.rows_sumary_,
                )
                for item in subitems_sumary:
                    self._process_sumary_item(item, pos, pos_, data)

    def _process_sumary_item(
        self,
        item: WebElementBot,
        pos: int,
        pos_: int,
        data: dict,
    ) -> None:
        """Processa um item do sumário e atualiza o dicionário de dados.

        Args:
            item: Elemento do sumário.
            pos (int): Posição do item.
            pos_ (int): Posição do grupo de sumário.
            data (dict): Dicionário de dados a ser atualizado.

        """
        if pos == 0 and pos_ == 0:
            num_proc = item.find_element(By.CLASS_NAME, el.numproc).text
            status_proc = "Em Andamento"
            with suppress(NoSuchElementException):
                status_proc = item.find_element(
                    By.CLASS_NAME,
                    el.statusproc,
                ).text
            data.update(
                {
                    "NUMERO_PROCESSO": num_proc,
                    "STATUS": status_proc.upper(),
                },
            )
            return

        value = None
        title = item.find_element(By.CLASS_NAME, el.nameitemsumary).text
        if title:
            title = title.upper()
        if " " in title:
            title = "_".join([ttl for ttl in title.split(" ") if ttl])

        with suppress(NoSuchElementException):
            value = item.find_element(By.CSS_SELECTOR, el.valueitemsumary).text

        if not value:
            with suppress(NoSuchElementException):
                element_search = el.value2_itemsumary.get(title)
                if element_search:
                    value = item.find_element(
                        By.CSS_SELECTOR,
                        element_search,
                    ).text
                    if title == "OUTROS_ASSUNTOS":
                        value = " ".join([
                            val for val in value.split(" ") if val
                        ])

        if value:
            data.update({title: value.upper()})

    def _extract_partes_information(self, data: dict) -> None:
        """Extraia informações das partes e atualize o dicionário de dados.

        Args:
            data (dict): Dicionário a ser atualizado com informações das partes.

        """
        table_partes = self.driver.find_element(By.ID, el.area_selecao)
        for group_parte in table_partes.find_elements(By.TAG_NAME, "tr"):
            self._process_group_parte(group_parte, data)

    def _process_group_parte(
        self,
        group_parte: WebElementBot,
        data: dict,
    ) -> None:
        """Processa um grupo de parte e atualiza o dicionário de dados.

        Args:
            group_parte: Elemento do grupo de parte.
            data (dict): Dicionário de dados a ser atualizado.

        """
        pos_repr = 0
        type_parte = self.format_string(
            group_parte.find_elements(By.TAG_NAME, "td")[0].text.upper(),
        )
        info_parte = group_parte.find_elements(By.TAG_NAME, "td")[1]
        info_parte_text = info_parte.text.split("\n")
        if "\n" in info_parte.text:
            for attr_parte in info_parte_text:
                if ":" in attr_parte:
                    representante = attr_parte.replace("  ", "").split(":")
                    tipo_representante = representante[0].upper()
                    nome_representante = representante[1].upper()
                    key = {
                        f"{tipo_representante}_{type_parte}": nome_representante,
                    }

                    doc_ = "Não consta"
                    with suppress(NoSuchElementException, IndexError):
                        doc_ = info_parte.find_elements(By.TAG_NAME, "input")[
                            pos_repr
                        ]
                        doc_ = doc_.get_attribute("value")

                    key_doc = {f"DOC_{tipo_representante}_{type_parte}": doc_}

                    pos_repr += 1

                    data.update(key)
                    data.update(key_doc)

                elif ":" not in attr_parte:
                    key = {type_parte: attr_parte}
                    data.update(key)

        elif "\n" not in info_parte_text:
            key = {type_parte: info_parte.text}
            data.update(key)
