"""Empty."""

from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from app.bots.elaw.cadastro._master import ElawCadastro
from app.decorators import shared_task
from app.decorators.bot import wrap_cls
from app.resources.elements import elaw as el

type_doc = {11: "cpf", 14: "cnpj"}


@shared_task(name="elaw.complementar_cadastro", bind=True, context=ContextTask)
@wrap_cls
class Complement(ElawCadastro):
    """Empty."""

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elaw_formats(value)

            if self.event_stop_bot.is_set():
                self.success = self.total_rows - pos
                break

            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        try:
            search = self.search(bot_data=self.bot_data)

            if not search:
                self.print_msg(
                    message="Processo não encontrado",
                    type_log="error",
                    row=self.row,
                )

                return

            start_time = time.perf_counter()
            message = "Inicializando complemento de cadastro"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            lista1 = list(self.bot_data.keys())
            check_esfera = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.label_esfera,
                )),
            )
            esfera_xls = self.bot_data.get("ESFERA")

            if esfera_xls and check_esfera.text.lower() != esfera_xls.lower():
                self.esfera(esfera_xls)

            for item in lista1:
                func = getattr(self, item.lower(), None)

                if func and item.lower() != "esfera":
                    func()

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            calc = execution_time / 60
            splitcalc = str(calc).split(".")
            minutes = int(splitcalc[0])
            seconds = int(float(f"0.{splitcalc[1]}") * 60)

            message = f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            self.validar_campos()
            self.validar_advs_participantes()
            self.salvar_tudo()

            if self.confirm_save():
                message = "Processo salvo com sucesso!"
                self.print_comprovante(message=message)

        except Exception as e:
            self.append_error(exc=e)
