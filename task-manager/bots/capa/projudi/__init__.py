"""Module: capa.

Extract and manage process details from Projudi by scraping and formatting data.
"""

import shutil
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from _interfaces.projudi import CapaProjudiDict
from common import raise_execution_error
from common.exceptions import ExecutionError

from ._1 import PrimeiraInstancia
from ._2 import SegundaInstancia


class Capa(PrimeiraInstancia, SegundaInstancia):
    """Extract process information from Projudi and populate structured data.

    This class extends CrawJUD to click through information panels,
    extract process data and participant details, and format them accordingly.
    """

    def execution(self) -> None:
        for pos, value in enumerate(self.frame):
            if self.bot_stopped.is_set():
                break

            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            try:
                driver = self.driver
                bot_data = self.bot_data

                self.print_message(
                    message=f"Buscando processo {bot_data['NUMERO_PROCESSO']}",
                    message_type="log",
                )

                search = self.search()
                trazer_copia = bot_data.get("TRAZER_COPIA", "não")
                if not search:
                    self.print_message(
                        message="Processo não encontrado.",
                        message_type="error",
                    )
                    return

                self.print_message(
                    message="Processo encontrado! Extraindo informações...",
                    message_type="info",
                )

                driver.refresh()
                self.get_process_informations()

                if trazer_copia and trazer_copia.lower() == "sim":
                    self.copia_pdf()

                self.print_message(
                    message="Informações extraídas com sucesso!",
                    message_type="success",
                )

            except ExecutionError as e:
                message_error = str(e)

                self.print_message(
                    message=f"{message_error}.",
                    message_type="error",
                )

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(data_save=[self.bot_data])

        self.finalize_execution()

    def get_process_informations(self) -> None:
        """Extrai informações detalhadas do processo da página atual do Projudi."""
        try:
            bot_data = self.bot_data
            numero_processo = bot_data.get("NUMERO_PROCESSO")

            callables = {"1": self.primeiro_grau, "2": self.segundo_grau}

            callables[str(bot_data.get("GRAU", "1"))](
                numero_processo=numero_processo,
            )

        except (ExecutionError, Exception):
            raise_execution_error("Erro ao executar operação")

    def primeiro_grau(self, numero_processo: str) -> None:
        process_info = CapaProjudiDict(NUMERO_PROCESSO=numero_processo)

        list_items = dir(CapaProjudiDict)
        for item in list_items:
            val = process_info.get(item)
            if (
                not val
                and not item.startswith("_")
                and not callable(getattr(CapaProjudiDict, item))
            ):
                process_info.update({item: "Vazio"})

        informacoes_gerais = self._informacoes_gerais_primeiro_grau()
        informacao_processo = self._info_processual_primeiro_grau()

        process_info.update(informacoes_gerais)
        process_info.update(informacao_processo)

        partes, advogados = self._partes_primeiro_grau(
            numero_processo=numero_processo
        )

        to_add = [
            ("Primeiro Grau", [process_info]),
            ("Partes", partes),
            ("Advogados", advogados),
        ]

        for item in to_add:
            self.append_success(work_sheet=item[0], data_save=item[1])

    def segundo_grau(self, numero_processo: str) -> None:
        process_info = CapaProjudiDict(NUMERO_PROCESSO=numero_processo)

        list_items = dir(CapaProjudiDict)
        for item in list_items:
            val = process_info.get(item)
            if (
                not val
                and not item.startswith("_")
                and not callable(getattr(CapaProjudiDict, item))
            ):
                process_info.update({item: "Vazio"})

        informacoes_gerais = self._informacoes_gerais_segundo_grau()
        informacao_processo = self._info_processual_segundo_grau()

        process_info.update(informacoes_gerais)
        process_info.update(informacao_processo)

        partes, advogados = self._partes_segundo_grau(
            numero_processo=numero_processo
        )

        to_add = [
            ("Segundo Grau", [process_info]),
            ("Partes", partes),
            ("Advogados", advogados),
        ]

        for item in to_add:
            self.append_success(work_sheet=item[0], data_save=item[1])

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
            self.print_message(
                message="Baixando cópia integral do processo...",
                message_type="log",
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
