"""Empty."""

from __future__ import annotations

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING, NoReturn

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import ExecutionError as ExecutionError
from crawjud.controllers.elaw import ElawBot
from crawjud.custom.task import ContextTask as ContextTask
from crawjud.decorators import shared_task as shared_task
from crawjud.decorators.bot import wrap_cls as wrap_cls
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot as WebElement

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


def raise_execution_error(message: str) -> NoReturn:
    """Lança exceção ExecutionError com mensagem informada ao validar campos obrigatórios.

    Args:
        message (str): Mensagem de erro a ser exibida na exceção.

    Raises:
        ExecutionError: Exceção lançada com a mensagem fornecida.

    """
    raise ExecutionError(message=message)


class ElawCadastro(ElawBot):
    """Empty."""

    def area_direito(self) -> None:
        wait = self.wait
        message = "Informando área do direito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        text = str(self.bot_data.get("AREA_DIREITO"))
        sleep(0.5)

        element_area_direito: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.css_label_area,
            )),
        )
        element_area_direito.select2(text)
        self.sleep_load('div[id="j_id_47"]')

        message = "Área do direito selecionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def subarea_direito(self) -> None:
        wait = self.wait
        message = "Informando sub-área do direito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        text = str(self.bot_data.get("SUBAREA_DIREITO"))
        sleep(0.5)

        element_subarea: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.comboareasub_css,
            )),
        )
        element_subarea.select2(text)

        self.sleep_load('div[id="j_id_4b"]')
        message = "Sub-Área do direito selecionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def next_page(self) -> None:
        next_page: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_button,
            )),
            message="Erro ao encontrar elemento",
        )
        next_page.click()

    def localizacao(self) -> None:
        text = "Judicial"

        message = "Informando esfera do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.css_esfera_judge)),
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Esfera Informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def esfera(self, text: str = "Judicial") -> None:
        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.css_esfera_judge)),
        )
        message = "Informando esfera do processo."
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.interact.sleep_load('div[id="j_id_48"]')

        message = "Esfera Informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def estado(self) -> None:
        key = "ESTADO"

        text = str(self.bot_data.get(key, None))

        message = "Informando estado do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.estado_input)),
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Estado do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def comarca(self) -> None:
        text = str(self.bot_data.get("COMARCA"))

        message = "Informando comarca do processo"
        type_log = "log"

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.comarca_input)),
        )
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Comarca do processo informado!"
        type_log = "log"

        self.print_msg(message=message, type_log=type_log, row=self.row)

    def foro(self) -> None:
        text = str(self.bot_data.get("FORO"))

        message = "Informando foro do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.foro_input)),
        )
        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Foro do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def advogado_interno(self) -> None:
        wait = self.wait
        driver = self.driver

        bot_data = self.bot_data

        message = "informando advogado interno"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        input_adv_responsavel: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.adv_responsavel,
            )),
        )
        input_adv_responsavel.click()
        input_adv_responsavel.send_keys(
            bot_data.get("ADVOGADO_INTERNO"),
        )

        id_input_adv = input_adv_responsavel.get_attribute("id").replace(
            "_input",
            "_panel",
        )
        css_wait_adv = f"span[id='{id_input_adv}'] > ul > li"

        wait_adv = None

        with suppress(TimeoutException):
            wait_adv: WebElement = WebDriverWait(driver, 25).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    css_wait_adv,
                )),
            )

        if wait_adv:
            wait_adv.click()
        elif not wait_adv:
            raise_execution_error(message="Advogado interno não encontrado")

        self.sleep_load('div[id="j_id_4b"]')

        self.sleep_load('div[id="j_id_4b"]')
        element_select: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.select_advogado_responsavel,
            )),
        )
        element_select.select2(bot_data.get("ADVOGADO_INTERNO"))

        id_element = element_select.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        driver.execute_script(comando)

        self.sleep_load('div[id="j_id_4b"]')

        message = "Advogado interno informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def vara(self) -> None:
        text = self.bot_data.get("VARA")

        wait = self.wait
        message = "Informando vara do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.vara_input)),
        )

        element_select.select2(text)

        self.sleep_load('div[id="j_id_4b"]')

        message = "Vara do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def validar_campos(self) -> None:
        message = "Validando campos"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        validar: dict[str, str] = {
            "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
        }
        message_campo: list[str] = []

        for campo in campos_validar:
            try:
                campo_validar: str = self.elements.dict_campos_validar.get(
                    campo,
                )
                command = f"return $('{campo_validar}').text()"
                element = self.driver.execute_script(command)

                if not element or element.lower() == "selecione":
                    raise_execution_error(
                        message=f'Campo "{campo}" não preenchido',
                    )

                message_campo.append(
                    f'<p class="fw-bold">Campo "{campo}" Validado | Texto: {element}</p>',
                )
                validar.update({campo.upper(): element})

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
        message_campo.append('<p class="fw-bold">Campos validados!</p>')
        message = "".join(message_campo)
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def validar_advogado(self) -> str:
        message = "Validando advogado responsável"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        campo_validar = self.elements.dict_campos_validar.get(
            "advogado_interno",
        )
        command = f"return $('{campo_validar}').text()"
        element = self.driver.execute_script(command)

        if not element or element.lower() == "selecione":
            message = 'Campo "Advogado Responsável" não preenchido'
            raise_execution_error(message=message)

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
            raise_execution_error(message=message)

        message = "Validando advogados participantes"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        tabela_advogados = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.tabela_advogados_resp,
        )

        not_adv = None
        with suppress(NoSuchElementException):
            tr_not_adv = self.elements.tr_not_adv
            not_adv = tabela_advogados.find_element(
                By.CSS_SELECTOR,
                tr_not_adv,
            )

        if not_adv is not None:
            message = "Sem advogados participantes!"
            raise_execution_error(message=message)

        advs = tabela_advogados.find_elements(By.TAG_NAME, "tr")

        for adv in advs:
            advogado = adv.find_element(By.TAG_NAME, "td").text
            if advogado.lower() == adv_name.lower():
                break

        else:
            message = "Advogado responsável não encontrado na lista de advogados participantes!"
            raise_execution_error(message=message)

        message = "Advogados participantes validados"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def confirm_save(self) -> bool:
        wait = self.wait
        driver = self.driver

        with suppress(TimeoutException):
            WebDriverWait(driver, 20).until(
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
                message="Erro ao encontrar elemento",
            )

            self.print_msg(
                message="Processo salvo com sucesso!",
                type_log="log",
                row=self.row,
            )
            return True

        mensagem_erro: str = None
        with suppress(TimeoutException, NoSuchElementException):
            mensagem_erro = (
                wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.div_messageerro_css,
                    )),
                    message="Erro ao encontrar elemento",
                )
                .find_element(By.TAG_NAME, "ul")
                .text
            )

        if not mensagem_erro:
            mensagem_erro = (
                "Cadastro do processo nao finalizado, verificar manualmente"
            )

        raise ExecutionError(mensagem_erro)

    def salvar_tudo(self) -> None:
        wait = self.wait

        self.sleep_load('div[id="j_id_4b"]')
        salvartudo: WebElement = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_salvar_proc,
            )),
            message="Erro ao encontrar elemento",
        )

        message = "Salvando processo novo"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        salvartudo.click()
