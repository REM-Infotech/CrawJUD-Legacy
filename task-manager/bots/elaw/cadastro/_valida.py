from contextlib import suppress
from time import sleep

from resources.elements import elaw as el
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .master import ElawBot

type ListStr = list[str]
campos_validar: ListStr = [
    "estado",
    "comarca",
    "foro",
    "vara",
    "divisao",
    "fase",
    "provimento",
    "fato_gerador",
    "objeto",
    "tipo_empresa",
    "tipo_entrada",
    "acao",
    "escritorio_externo",
    "classificacao",
    "toi_criado",
    "nota_tecnica",
    "liminar",
]


class ElawValidacao(ElawBot):
    def validar_campos(self) -> None:
        message = "Validando campos"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        validar: dict[str, str] = {
            "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
        }

        for campo in campos_validar:
            try:
                campo_validar: str = el.DICT_CAMPOS_VALIDAR.get(
                    campo,
                )
                command = f"return $('{campo_validar}').text()"
                element = self.driver.execute_script(command)

                if not element or element.lower() == "selecione":
                    _raise_execution_error(
                        message=f'Campo "{campo}" não preenchido',
                    )

                message = f'Campo "{campo}" Validado | Texto: {element}'
                self.print_msg(message=message, type_log="info", row=self.row)

            except Exception as e:
                try:
                    message = e.message

                except Exception:
                    message = str(e)

                validar.update({campo.upper(): message})

                message = message
                type_log = "info"
                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
                )

        self.append_validarcampos([validar])
        message = "Campos validados!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def validar_advogado(self) -> str:
        message = "Validando advogado responsável"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        campo_validar = el.DICT_CAMPOS_VALIDAR.get(
            "advogado_interno",
        )
        command = f"return $('{campo_validar}').text()"
        element = self.driver.execute_script(command)

        if not element or element.lower() == "selecione":
            message = 'Campo "Advogado Responsável" não preenchido'
            _raise_execution_error(message=message)

        message = f'Campo "Advogado Responsável" | Texto: {element}'
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        sleep(0.5)

        return element

    def validar_advs_participantes(self) -> None:
        data_bot = self.bot_data
        adv_name = data_bot.get("ADVOGADO_INTERNO", self.validar_advogado())

        if not adv_name.strip():
            message = "Necessário advogado interno para validação!"
            _raise_execution_error(message=message)

        message = "Validando advogados participantes"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        tabela_advogados = self.driver.find_element(
            By.CSS_SELECTOR,
            el.tabela_advogados_resp,
        )

        not_adv = None
        with suppress(NoSuchElementException):
            tr_not_adv = el.tr_not_adv
            not_adv = tabela_advogados.find_element(
                By.CSS_SELECTOR,
                tr_not_adv,
            )

        if not_adv is not None:
            message = "Sem advogados participantes!"
            _raise_execution_error(message=message)

        advs = tabela_advogados.find_elements(By.TAG_NAME, "tr")

        for adv in advs:
            advogado = adv.find_element(By.TAG_NAME, "td").text
            if advogado.lower() == adv_name.lower():
                break

        else:
            message = "Advogado responsável não encontrado na lista de advogados participantes!"
            _raise_execution_error(message=message)

        message = "Advogados participantes validados"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)
