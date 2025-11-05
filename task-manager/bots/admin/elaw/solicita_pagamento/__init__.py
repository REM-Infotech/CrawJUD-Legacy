"""Module for managing payment solution processes within the ELAW system.

This module provides functionality to handle payment management and solution creation within
the ELAW system. It enables automated payment processing, validations, and record-keeping.

Classes:
    SolPags: Handles payment solutions by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

from typing import TYPE_CHECKING

from bots.resources._formatadores import formata_string
from common._raises import raise_execution_error

from ._master import ElawPagamentos

if TYPE_CHECKING:
    from collections.abc import Callable


class SolicitaPgto(ElawPagamentos):
    """Gerencie solicitações de pagamento automatizadas no sistema ELAW.

    Esta classe estende ElawPagamentos para processar solicitações de pagamento,
    realizando automação de etapas, validações e registro de resultados.

    Métodos:
        execution() -> None: Execute o fluxo principal de solicitações de pagamento.
        queue() -> None: Realize o processamento individual de cada solicitação.

    """

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)
        self.driver.maximize_window()
        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elawFormats(value)
            if self.bot_stopped.is_set():
                break

            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        try:
            search = self.search()

            if not search:
                raise_execution_error(message="Processo não encontrado!")
            namedef = formata_string(self.bot_data.get("TIPO_PAGAMENTO"))
            self.novo_pagamento()
            self.seleciona_tipo_pagamento(namedef)
            pgto: Callable[..., None] = getattr(self, namedef.lower())
            pgto()

            self.save_changes()
            self.append_success(self.confirm_save())

        except Exception as e:
            message_error = str(e)

            self.print_message(
                message=f"{message_error}.",
                message_type="error",
            )

            self.bot_data.update({"MOTIVO_ERRO": message_error})
            self.append_error(data_save=[self.bot_data])
