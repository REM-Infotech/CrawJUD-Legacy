"""Module: movimentacao.

Handle movement-related operations in the Projudi system with data scraping and reporting.
"""

from __future__ import annotations

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING, ClassVar

from httpx import Client
from pypdf import PdfReader, PdfWriter
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.projudi import ProjudiBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import projudi as el

if TYPE_CHECKING:
    from pathlib import Path

    from crawjud.utils.webdriver.web_element import WebElementBot


@shared_task(name="projudi.movimentacao", bind=True, base=ContextTask)
@wrap_cls
class Movimentacao(ProjudiBot):
    """Manage movements in Projudi by scraping, filtering, and logging process-related actions.

    This class extends CrawJUD to handle operations including movement search,
    keyword filtering, and report generation for movement activities.
    """

    movimentacao_encontrada: ClassVar[bool] = False
    list_movimentacoes_extraidas: ClassVar[list[dict[str, str]]] = []

    def execution(self) -> None:
        """Loop through data rows and process each movement with error management.

        Iterates over data frame entries and queues movement processing.
        """
        frame = self.frame
        self._total_rows = len(frame)

        for pos, value in enumerate(frame):
            if self.event_stop_bot.is_set():
                break

            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except (ExecutionError, Exception) as e:
                message_error = str(e)

                self.print_msg(message=f"{message_error}.", type_log="error")
                self.append_error(self.bot_data)

                self.message_error = None

        self.queue_save_xlsx.put({
            "to_save": self.list_movimentacoes_extraidas,
            "sheet_name": "Movimentações Extraídas",
        })
        self.finalize_execution()

    def queue(self) -> None:
        """Manage queuing of movement operations and scrape required data.

        Raises:
            ExecutionError: If processing fails during movement queue operations.

        """
        try:
            bot_data = self.bot_data
            self.appends = []
            self.another_append: list[tuple[dict, str, str]] = []
            self.resultados = []

            self.table_moves = None

            list_botdata = list(self.bot_data.items())
            for key, value in list_botdata:
                if value is None:
                    self.bot_data.pop(key)

            self.print_msg(
                message=f"Buscando processo {bot_data['NUMERO_PROCESSO']}",
                type_log="log",
                row=self.row,
            )

            search = self.search()

            if search is not True:
                self.print_msg(
                    message="Processo não encontrado!",
                    row=self.row,
                    type_log="error",
                )
                return

            self.print_msg(
                message="Processo Encontrado! Buscando movimentações...",
                type_log="log",
                row=self.row,
            )

            self.set_page_size()
            self.extrair_movimentacoes()

        except (ExecutionError, Exception) as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

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

    def extrair_movimentacoes(self) -> None:
        """Extrai e processa as movimentações do processo no sistema Projudi.

        Realiza a raspagem das movimentações do processo atualmente selecionado,
        processando e armazenando os dados relevantes para posterior análise.

        """
        wait = self.wait
        wait._timeout = 10

        _driver = self.driver

        bot_data = self.bot_data

        table_movimentacoes = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, el.table_moves),
            ),
        )

        palavras_chave = bot_data["PALAVRAS_CHAVE"]
        termos = [
            " ".join(termo.split())
            for termo in (
                [palavras_chave]
                if "," not in palavras_chave
                else palavras_chave.split(",")
            )
        ]

        def filtrar(elemento: WebElementBot) -> bool:
            """Filtre elementos de movimentação conforme os termos especificados.

            Args:
                elemento (WebElementBot): Elemento da tabela de movimentações.

            Returns:
                bool: Indica se o elemento corresponde aos termos filtrados.

            """
            return any(
                elemento.find_elements(By.TAG_NAME, "td")[3].text.lower()
                == termo.lower()
                for termo in termos
            ) or any(
                termo.lower()
                in elemento.find_elements(By.TAG_NAME, "td")[3].text.lower()
                for termo in termos
            )

        self.__iter_movimentacoes(
            com_documento=True,
            table_movimentacoes=table_movimentacoes,
            filtered_moves=list(
                filter(
                    filtrar,
                    table_movimentacoes.find_elements(
                        By.XPATH,
                        el.list_moves_comarquivo,
                    ),
                ),
            ),
        )
        self.__iter_movimentacoes(
            table_movimentacoes=table_movimentacoes,
            filtered_moves=list(
                filter(
                    filtrar,
                    table_movimentacoes.find_elements(
                        By.XPATH,
                        el.list_moves_semarquivo,
                    ),
                ),
            ),
        )

        if not self.movimentacao_encontrada:
            self.print_msg(
                message="Nenhuma movimentação encontrada!",
                row=self.row,
                type_log="error",
            )
            return

        self.print_msg(
            message="Movimentações extraídas com sucesso!",
            row=self.row,
            type_log="success",
        )
        self.movimentacao_encontrada = False

    def __iter_movimentacoes(
        self,
        table_movimentacoes: WebElementBot,
        filtered_moves: list[WebElementBot],
        *,
        com_documento: bool = False,
    ) -> None:
        bot_data = self.bot_data
        qtd_movimentacoes = len(filtered_moves)
        if qtd_movimentacoes > 0:
            self.movimentacao_encontrada = True

            message = f"Foram encontradas {qtd_movimentacoes} movimentações!"

            if com_documento:
                message = f"Foram encontradas {qtd_movimentacoes} movimentações com arquivos!"

            self.print_msg(
                message=message,
                row=self.row,
                type_log="info",
            )

        for item in filtered_moves:
            tds = item.find_elements(By.TAG_NAME, "td")
            self._formatar_dados(tds)
            if all(
                [
                    com_documento,
                    "TRAZER_ARQUIVO_MOVIMENTACAO" in bot_data,
                    bot_data["TRAZER_ARQUIVO_MOVIMENTACAO"].lower() == "sim",
                ],
            ):
                self._extrair_arquivos_movimentacao(
                    table_movimentacoes=table_movimentacoes,
                    tds=tds,
                )

    def _extrair_arquivos_movimentacao(
        self,
        table_movimentacoes: WebElementBot,
        tds: list[WebElementBot],
    ) -> None:
        """Extraia arquivos vinculados à movimentação do processo no Projudi.

        Args:
            table_movimentacoes (WebElementBot): Elemento da tabela de movimentações.
            tds (list[WebElementBot]): Lista de elementos <td> da movimentação.

        """
        driver = self.driver
        bot_data = self.bot_data
        out_dir = self.output_dir_path

        numero_processo = bot_data["NUMERO_PROCESSO"]
        btn_show_files = tds[0].find_element(By.TAG_NAME, "a")

        btn_show_files.click()

        class_btn = btn_show_files.get_attribute("class")
        id_rowmovimentacao = class_btn.replace("linkArquivos", "row")
        arquivo_movimentacao = table_movimentacoes.find_element(
            By.CSS_SELECTOR,
            f'tr[id="{id_rowmovimentacao}"]',
        )

        sleep(3)
        table_files = arquivo_movimentacao.find_element(By.TAG_NAME, "table")

        cookies = {
            str(cookie["name"]): str(cookie["value"])
            for cookie in driver.get_cookies()
        }

        part_files: list[Path] = []
        writer = PdfWriter()
        with Client(cookies=cookies) as client:
            for pos, tr_file in enumerate(
                table_files.find_elements(By.TAG_NAME, "tr"),
            ):
                tds_files = tr_file.find_elements(By.TAG_NAME, "td")
                tds_files[0]

                link_arquivo = (
                    tds_files[4]
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                )

                with client.stream("get", link_arquivo) as stream:
                    tmp_file_name = f"part_{str(pos).zfill(2)}.pdf"
                    tmp_path_file = out_dir.joinpath(tmp_file_name)

                    with tmp_path_file.open("wb") as file:
                        for chunk in stream.iter_bytes(chunk_size=8192):
                            file.write(chunk)

                    part_files.append(tmp_path_file)

        _pages = [
            writer.add_page(page)
            for f in part_files
            for page in PdfReader(f).pages
        ]

        pdf_out_name = tds[3].text
        if "\n" in pdf_out_name:
            pdf_out_name = pdf_out_name.split("\n")[0]

        pdf_out_name = " ".join(pdf_out_name.split())
        pdf_name = f"{numero_processo} - {pdf_out_name} - {self.pid}.pdf"

        path_pdf = self.output_dir_path.joinpath(pdf_name)
        with path_pdf.open("wb") as fp:
            writer.write(fp)

        with suppress(Exception):
            for file in part_files:
                file.unlink()

    def _formatar_dados(
        self,
        tds: list[WebElementBot],
    ) -> None:
        """Formata e armazene os dados da movimentação extraída do Projudi.

        Args:
            tds (list[WebElementBot]): Lista de elementos `<td>` da movimentação.

        """
        bot_data = self.bot_data

        evento = tds[3].text
        movimentado_por = tds[4].text

        dados = {
            "Número do Processo": bot_data["NUMERO_PROCESSO"],
            "Seq.": tds[1].text.strip(),
            "Data": tds[2].text,
            "Evento": " ".join(evento.split()),
            "Descrição Evento": "Sem Descrição",
            "Movimentado Por": " ".join([
                t.capitalize() for t in movimentado_por.split()
            ]),
        }

        if "\n" in movimentado_por:
            movimentador_split = movimentado_por.split("\n")
            movimentador = " ".join(movimentador_split[0].split())
            classificacao = movimentador_split[1]
            dados.update({
                "Movimentado Por": movimentador,
                "Classificação": " ".join(classificacao.split()),
            })

        if "\n" in evento:
            evento_e_descricaco = evento.split("\n")

            dados.update({
                "Evento": " ".join(evento_e_descricaco[0].split()),
                "Descrição Evento": " ".join(evento_e_descricaco[1].split()),
            })

        self.list_movimentacoes_extraidas.append(dados)
