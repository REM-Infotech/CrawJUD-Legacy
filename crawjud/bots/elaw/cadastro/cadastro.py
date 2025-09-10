"""Modulo Elaw Pré Cadastro."""

from __future__ import annotations

import time

from selenium.webdriver.common.by import By

from crawjud.bots.elaw.cadastro._master import ElawCadastro
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import elaw as el


@shared_task(name="elaw.cadastro", bind=True, context=ContextTask)
@wrap_cls
class Cadastro(ElawCadastro):
    """The Cadastro class extends CrawJUD to manage registration tasks within the application.

    Attributes:
        type_doc (dict): A dictionary mapping document types to their identifiers.
        ...existing attributes...

    """

    def execution(self) -> None:
        """Execute the main processing loop for registrations.

        Iterates over each entry in the data frame and processes it.
        Handles authentication and error logger.

        """
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elaw_formats(value)
            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        try:
            driver = self.driver
            search = self.search(bot_data=self.bot_data)

            if search:
                message = "Processo já cadastrado!"
                type_log = "error"
                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
                )
                self.append_success()
                return

            message = "Processo não encontrado, inicializando cadastro..."
            type_log = "log"
            self.print_msg(
                message=message,
                type_log=type_log,
                row=self.row,
            )

            btn_newproc = driver.find_element(
                By.CSS_SELECTOR,
                el.botao_novo,
            )
            btn_newproc.click()

            start_time = time.perf_counter()

            self.area_direito()
            self.subarea_direito()
            self.next_page()
            self.localizacao()
            self.estado()
            self.comarca()
            self.foro()
            self.vara()
            self.proceso()
            self.empresa()
            self.parte_contraria()
            self.capital_interior()
            self.acao()
            self.advogado_interno()
            self.adv_parte_contraria()
            self.data_distribuicao()
            self.valor_causa()
            self.escritorio_externo()
            self.tipo_contingencia()

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            calc = execution_time / 60
            splitcalc = str(calc).split(".")
            minutes = int(splitcalc[0])
            seconds = int(float(f"0.{splitcalc[1]}") * 60)

            message = f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
            type_log = "log"
            self.print_msg(
                message=message,
                type_log=type_log,
                row=self.row,
            )

            self.salvar_tudo()

            if self.confirm_save() is True:
                message = "Processo salvo com sucesso!"
                self.print_comprovante(message=message)

        except Exception as e:
            self.append_error(exc=e)
