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
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo  # noqa: F401

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


@shared_task(name="projudi.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa(ProjudiBot):
    """Extract process information from Projudi and populate structured data.

    This class extends CrawJUD to click through information panels,
    extract process data and participant details, and format them accordingly.
    """

    def execution(self) -> None:
        """Execute the main processing loop to extract process information.

        Iterates over each data row and queues process data extraction.
        """
        frame = self.frame
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
            search = self.search()
            trazer_copia = self.bot_data.get("TRAZER_COPIA", "não")
            if not search:
                _raise_execution_error("Processo não encontrado")

            self.driver.refresh()
            data = self.get_process_informations()

            if trazer_copia and trazer_copia.lower() == "sim":
                data = self.copia_pdf(data)

            self.queue_save_xlsx.put({
                "to_save": [data],
                "sheet_name": "Capa",
            })

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

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

            def primeiro_grau() -> dict[str, str | int | datetime]:
                process_info: dict[str, str | int | datetime] = {
                    "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
                }
                process_info.update(self._informacoes_gerais_primeiro_grau())
                process_info.update(
                    self._informacoes_processuais_primeiro_grau(),
                )
                return process_info

            callables = {"1": primeiro_grau}

            return callables[str(bot_data.get("GRAU", "1"))]()

        except (ExecutionError, Exception):
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

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

    def _informacoes_processuais_primeiro_grau(self) -> dict[str, str]:
        wait = self.wait

        table_info_processual = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.info_processual_primeiro_grau,
            )),
        )

        inner_html = table_info_processual.get_attribute("innerHTML")
        return self.parse_data(inner_html=inner_html)
