"""Module: movimentacao.

Handle movement-related operations in the Projudi system with data scraping and reporting.
"""

from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import ClassVar

from httpx import Client
from pypdf import PdfReader, PdfWriter
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from bots.projudi.master import ProjudiBot
from bots.resources.driver.web_element import WebElementBot
from bots.resources.elements import projudi as el
from common.exceptions import ExecutionError


class Movimentacao(ProjudiBot):
    """Gerencie movimentações no Projudi por raspagem e registro de ações processuais.

    Esta classe estende CrawJUD para realizar operações como busca de movimentações,
    filtragem por palavras-chave e geração de relatórios das atividades processuais.
    """

    movimentacao_encontrada: ClassVar[bool] = False
    list_movimentacoes_extraidas: ClassVar[list[dict[str, str]]] = []

    def execution(self) -> None:
        """Execute o processamento das linhas de dados e trate erros de movimentação.

        Percorra as entradas do frame de dados, processando cada movimentação e
        gerenciando possíveis exceções durante a execução.

        """
        frame = self.frame
        self._total_rows = len(frame)

        for pos, value in enumerate(frame):
            if self.bot_stopped.is_set():
                break

            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            try:
                self.queue()

            except (ExecutionError, Exception) as e:
                message_error = str(e)

                self.print_message(
                    message=f"{message_error}.",
                    message_type="error",
                )

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(data_save=[self.bot_data])

        self.finalize_execution()

    def queue(self) -> None:
        """Gerencie a fila de operações de movimentação e realize a raspagem de dados.

        Raises:
            ExecutionError: Caso ocorra falha durante o processamento da fila.

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

            self.print_message(
                message=f"Buscando processo {bot_data['NUMERO_PROCESSO']}",
                message_type="log",
            )

            search = self.search()

            if search is not True:
                self.print_message(
                    message="Processo não encontrado!",
                    message_type="error",
                )
                return

            self.print_message(
                message="Processo Encontrado! Buscando movimentações...",
                message_type="log",
            )

            self.set_page_size()
            self.extrair_movimentacoes()

        except (ExecutionError, Exception) as e:
            raise ExecutionError(exc=e) from e

    def set_page_size(self) -> None:
        """Defina o tamanho da página da tabela de movimentações para 1000 registros."""
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
        """Extraia e processe as movimentações do processo no sistema Projudi.

        Realize a raspagem das movimentações do processo atualmente selecionado,
        processando e armazenando os dados relevantes para análise posterior.

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
            self.print_message(
                message="Nenhuma movimentação encontrada!",
                message_type="error",
            )
            return

        self.print_message(
            message="Movimentações extraídas com sucesso!",
            message_type="success",
        )
        self.movimentacao_encontrada = False

    def __iter_movimentacoes(
        self,
        table_movimentacoes: WebElementBot,
        filtered_moves: list[WebElementBot],
        *,
        com_documento: bool = False,
    ) -> None:
        """Itera sobre as movimentações filtradas e processe cada uma conforme regras.

        Args:
            table_movimentacoes (WebElementBot): Elemento da tabela de movimentações.
            filtered_moves (list[WebElementBot]): Lista de linhas filtradas.
            com_documento (bool, opcional): Indica se deve extrair arquivos. Padrão: False.

        """
        bot_data = self.bot_data
        qtd_movimentacoes = len(filtered_moves)
        if qtd_movimentacoes > 0:
            self.movimentacao_encontrada = True

            message = f"Foram encontradas {qtd_movimentacoes} movimentações!"

            if com_documento:
                message = f"Foram encontradas {qtd_movimentacoes} movimentações com arquivos!"

            self.print_message(
                message=message,
                message_type="info",
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
