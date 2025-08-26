"""Module: capa.

Extract and manage process details from Projudi by scraping and formatting data.
"""

from __future__ import annotations

import re  # noqa: F401
import shutil
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar
from zoneinfo import ZoneInfo  # noqa: F401

from bs4 import BeautifulSoup
from selenium.common.exceptions import (
    StaleElementReferenceException,  # noqa: F401
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.projudi import ProjudiBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import projudi as el

if TYPE_CHECKING:
    from datetime import datetime

    from selenium.webdriver.remote.webelement import WebElement  # noqa: F401

type ListPartes = list[tuple[list[dict[str, str]], list[dict[str, str]]]]


@shared_task(name="projudi.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa(ProjudiBot):
    """Extract process information from Projudi and populate structured data.

    This class extends CrawJUD to click through information panels,
    extract process data and participant details, and format them accordingly.
    """

    list_partes: ClassVar[ListPartes] = []

    def execution(self) -> None:
        """Execute the main processing loop to extract process information.

        Iterates over each data row and queues process data extraction.
        """
        frame = self.frame

        self._total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            try:
                self.queue()

            except ExecutionError as e:
                message_error = str(e)

                self.print_msg(
                    message=f"{message_error}.",
                    type_log="error",
                )

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the process information extraction queue by refreshing the driver.

        Raises:
            ExecutionError: If the process is not found or extraction fails.

        """
        try:
            driver = self.driver
            bot_data = self.bot_data

            self.print_msg(
                message=f"Buscando processo {bot_data['NUMERO_PROCESSO']}",
                row=self.row,
                type_log="log",
            )

            search = self.search()
            trazer_copia = bot_data.get("TRAZER_COPIA", "não")
            if not search:
                self.print_msg(
                    message="Processo não encontrado.",
                    row=self.row,
                    type_log="error",
                )
                return

            self.print_msg(
                message="Processo encontrado! Extraindo informações...",
                row=self.row,
                type_log="info",
            )

            driver.refresh()
            data = self.get_process_informations()

            if trazer_copia and trazer_copia.lower() == "sim":
                data = self.copia_pdf(data)

            self.queue_save_xlsx.put({
                "to_save": [data],
                "sheet_name": "Capa",
            })

            for list_parte, list_representantes in self.list_partes:
                if list_parte:
                    self.queue_save_xlsx.put(
                        self.queue_save_xlsx.put({
                            "to_save": list_parte,
                            "sheet_name": "Partes",
                        }),
                    )

                if list_representantes:
                    self.queue_save_xlsx.put(
                        self.queue_save_xlsx.put({
                            "to_save": list_representantes,
                            "sheet_name": "Partes",
                        }),
                    )

            self.list_partes.clear()

            self.print_msg(
                message="Informações extraídas com sucesso!",
                row=self.row,
                type_log="success",
            )

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def copia_pdf(
        self,
        data: dict[str, str | int | datetime],
    ) -> dict[str, str | int | datetime]:
        """Extract the movements of the legal proceedings and saves a PDF copy.

        Returns:
             dict[str, str | int | datetime]: Data return

        """
        id_proc = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[name="id"]',
        ).get_attribute("value")

        btn_exportar = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[id="btnMenuExportar"]',
            )),
        )
        time.sleep(0.5)
        btn_exportar.click()

        btn_exportar_processo = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[id="exportarProcessoButton"]'),
            ),
        )
        time.sleep(0.5)
        btn_exportar_processo.click()

        def unmark_gen_mov() -> None:
            time.sleep(0.5)
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="gerarMovimentacoes"][value="false"]',
                )),
            ).click()

        def unmark_add_validate_tag() -> None:
            time.sleep(0.5)
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="adicionarTarjaValidacao"][value="false"]',
                )),
            ).click()

        def export() -> None:
            self.print_msg(
                message="Baixando cópia integral do processo...",
                type_log="log",
            )

            time.sleep(5)

            n_processo = self.bot_data.get("NUMERO_PROCESSO")
            path_pdf = Path(self.output_dir_path).joinpath(
                f"Cópia Integral - {n_processo} - {self.pid}.pdf",
            )

            btn_exportar = self.driver.find_element(
                By.CSS_SELECTOR,
                'input[name="btnExportar"]',
            )
            btn_exportar.click()

            count = 0
            time.sleep(5)
            path_copia = self.output_dir_path.joinpath(
                f"{id_proc}.pdf",
            ).resolve()

            while count <= 300:
                if path_copia.exists():
                    break

                time.sleep(2)
                count += 1

            if not path_copia.exists():
                raise ExecutionError(message="Arquivo não encontrado!")

            shutil.move(path_copia, path_pdf)

            time.sleep(0.5)
            data.update({"CÓPIA_INTEGRAL": path_pdf.name})

        unmark_gen_mov()
        unmark_add_validate_tag()
        export()

        return data

    def get_process_informations(self) -> dict[str, str | int | datetime]:
        """Extrai informações detalhadas do processo da página atual do Projudi.

        Returns:
            dict[str, str | int | datetime]: Dicionário com informações formatadas do processo.

        """
        process_info: dict[str, str | int | datetime] = None
        try:
            bot_data = self.bot_data
            numero_processo = bot_data.get("NUMERO_PROCESSO")

            def primeiro_grau(
                numero_processo: str,
            ) -> dict[str, str | int | datetime]:
                process_info: dict[str, str | int | datetime] = {
                    "Número do processo": numero_processo,
                }
                process_info.update(self._informacoes_gerais_primeiro_grau())
                process_info.update(self._info_processual_primeiro_grau())

                self.list_partes = self._partes_primario_grau(
                    numero_processo=numero_processo,
                )

                return process_info

            callables = {"1": primeiro_grau}

            return callables[str(bot_data.get("GRAU", "1"))](
                numero_processo=numero_processo,
            )

        except (ExecutionError, Exception):
            _raise_execution_error("Erro ao executar operação")

        return process_info

    def _informacoes_gerais_primeiro_grau(self) -> None:
        wait = self.wait

        info_geral = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'li[id="tabItemprefix0"]',
            )),
        )

        info_geral.click()

        table_info_geral = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.info_geral_table_primeiro_grau,
            )),
        )

        inner_html = table_info_geral.get_attribute("innerHTML")
        return self.parse_data(inner_html=inner_html)

    def _info_processual_primeiro_grau(self) -> dict[str, str]:
        wait = self.wait

        table_info_processual = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.info_processual_primeiro_grau,
            )),
        )

        inner_html = table_info_processual.get_attribute("innerHTML")
        return self.parse_data(inner_html=inner_html)

    def _partes_primario_grau(
        self,
        numero_processo: str,
    ) -> list[tuple[list[dict[str, str]], list[dict[str, str]]]]:
        wait = self.wait

        btn_partes = wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.btn_partes)),
        )

        btn_partes.click()
        list_partes: list[
            tuple[list[dict[str, str]], list[dict[str, str]]]
        ] = []
        grouptable_partes = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.partes_primeiro_grau,
            )),
        )

        for table in grouptable_partes.find_elements(By.TAG_NAME, "table"):
            tbody_table = table.find_element(By.TAG_NAME, "tbody")
            inner_html = tbody_table.get_attribute("innerHTML")
            list_partes.append(
                self._partes_projudi(
                    inner_html=inner_html,
                    numero_processo=numero_processo,
                ),
            )

        return list_partes

    def _partes_projudi(
        self,
        inner_html: str,
        numero_processo: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """Extraia informações das partes do processo na tabela do Projudi.

        Args:
            inner_html (str): HTML da página contendo a tabela de partes.
            numero_processo(str): Numero processo

        Returns:
            (tuple[list[dict[str, str]], list[dict[str, str]]]):
                Lista de dicionários com dados das partes.

        """
        soup = BeautifulSoup(inner_html, "html.parser")
        partes: list[dict[str, str]] = []
        advogados: list[dict[str, str]] = []
        endereco = ""

        # Encontra todas as linhas principais das partes
        for tr in soup.find_all("tr", class_="even"):
            tds = tr.find_all("td")
            if not tds or len(tds) < 6:
                continue
            # Extrai nome
            nome = str(tds[1].get_text(strip=True))
            # Extrai documento (RG ou similar)
            documento = str(tds[2].get_text(strip=True))
            # Extrai CPF
            cpf = str(tds[3].get_text(strip=True))
            # Extrai OABs e advogados
            advs = ", ".join([
                " ".join(str(li.get_text(" ", strip=True)).split())
                for li in tds[5].find_all("li")
            ])

            # Busca o id da linha expandida para endereço
            row_id = tr.get("id")
            if row_id:
                row_detalhe = soup.find("tr", id=f"row{row_id}")
                if row_detalhe:
                    endereco_div = row_detalhe.find(
                        "div",
                        class_="extendedinfo",
                    )
                    if endereco_div:
                        endereco = str(endereco_div.get_text(" ", strip=True))

            if nome != "Descrição:":
                for li in tds[5].find_all("li"):
                    advogado_e_oab = " ".join(
                        str(li.get_text(" ", strip=True)).split(),
                    ).split(" - ")

                    advogados.append({
                        "Número do processo": numero_processo,
                        "Nome": advogado_e_oab[1],
                        "OAB": advogado_e_oab[0],
                        "Representado": nome,
                    })

                partes.append({
                    "Número do processo": numero_processo,
                    "Nome": nome,
                    "Documento": documento,
                    "Cpf": cpf,
                    "Advogados": advs,
                    "Endereco": endereco,
                })

        return partes, advogados
