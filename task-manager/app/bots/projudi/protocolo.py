"""Módulo de protocolo do bot Projudi.

Automatiza o protocolo de processos no sistema Projudi.
"""

from __future__ import annotations

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING, NoReturn

import dotenv
from PIL import Image
from selenium.common.exceptions import (
    TimeoutException,
)
from selenium.webdriver import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from app.common.exceptions.bot import FileError
from app.common.exceptions.bot.projudi import PasswordTokenError
from app.common.exceptions.selenium_webdriver import SeleniumError
from app.controllers.projudi import ProjudiBot
from app.custom.task import ContextTask
from app.decorators import shared_task
from app.decorators.bot import wrap_cls
from app.interfaces.types.bots import DataSucesso
from app.resources import format_string
from app.resources.elements import projudi as el

if TYPE_CHECKING:
    from app.utils.webdriver.web_element import WebElementBot

dotenv.load_dotenv()


def raise_password_token() -> NoReturn:
    """Password token error.

    Raises:
        PasswordTokenError: PasswordTokenError

    """
    raise PasswordTokenError(message="Senha Incorreta!")


@shared_task(name="projudi.protocolo", bind=True, base=ContextTask)
@wrap_cls
class Protocolo(ProjudiBot):
    """Executa o protocolo de processos no Projudi.

    Herda de ProjudiBot e implementa a lógica de protocolo.
    """

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.event_stop_bot.is_set():
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        data: DataSucesso = {}

        try:
            search = self.search()

            if not search:
                return

            self.__entra_pagina_protocolo()
            self.__informa_tipo_protocolo()
            self.__adicionar_arquivos()

            sleep(0.5)

            self.__seleciona_parte_interessada()

            sleep(0.5)

            self.__finaliza_peticionamento()

            if self.__confirma_protocolo():
                data = self.__screenshot_sucesso()

        except PasswordTokenError as e:
            self.append_error(exc=e)

        except SeleniumError as e:
            self.append_error(exc=e)

        except Exception as e:
            self.append_error(exc=e)

        if data:
            self.append_success(data)

    def __entra_pagina_protocolo(self) -> None:
        """Empty."""
        self.print_msg(
            message="Inicializando Protocolo",
            type_log="log",
            row=self.row,
        )

        wait = WebDriverWait(self.driver, 10)

        btn_peticionar = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_BTN_PETICIONAR,
            )),
        )

        btn_peticionar.click()

    def __informa_tipo_protocolo(self) -> None:
        """Empty."""
        bot_data = self.bot_data

        self.print_msg(
            message="Informando Tipo da movimentação",
            type_log="log",
            row=self.row,
        )

        wait = WebDriverWait(self.driver, 10)

        tipo_protocolo = bot_data["TIPO_PROTOCOLO"]

        campo_tipo_protocolo = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_INPUT_TIPO_PROTOCOLO,
            )),
        )

        campo_tipo_protocolo.send_keys(tipo_protocolo)
        sleep(0.5)
        campo_tipo_protocolo.send_keys(Keys.ENTER)
        sleep(0.5)

    def __seleciona_parte_interessada(self) -> None:
        """Empty."""
        self.print_msg(
            message="Selecionando parte representada",
            type_log="log",
            row=self.row,
        )

        bot_data = self.bot_data

        wait = WebDriverWait(self.driver, 10)

        polo_parte = bot_data["POLO_PARTE"]
        nome_parte = bot_data["PARTE_PETICIONANTE"]

        xpath_polo = el.XPATH_RADIO_POLO_PARTE.format(
            POLO_PARTE=polo_parte.capitalize(),
        )
        xpath_parte = el.XPATH_CHECKBOX_PARTE.format(NOME_PARTE=nome_parte)

        radio_polo_parte = wait.until(
            ec.presence_of_element_located((By.XPATH, xpath_polo)),
        )

        radio_polo_parte.click()

        checkbox_parte = wait.until(
            ec.element_to_be_clickable((By.XPATH, xpath_parte)),
        )

        checkbox_parte.click()

    def __adicionar_arquivos(self) -> None:
        """Empty."""
        bot_data = self.bot_data
        self.print_msg(
            message="Adicionando arquivos...",
            type_log="log",
            row=self.row,
        )

        wait = WebDriverWait(self.driver, 10)

        btn_arquivos = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_BTN_ENTRAR_TELA_ARQUIVOS,
            )),
        )
        btn_arquivos.click()

        main_window = self.driver.current_window_handle
        wait.until(
            ec.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")),
        )

        self.__check_contains_files()
        self.__peticao_principal()

        if bot_data.get("ANEXOS"):
            self.__anexos_adicionais()

        self.__assinar()
        self.__confirma_inclusao()

        self.driver.switch_to.window(main_window)

    def __check_contains_files(self) -> None:
        """Empty."""
        contem_arquivos = True
        wait = WebDriverWait(self.driver, 10)
        table_arquivos = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_TABLE_ARQUIVOS,
            )),
        )

        with suppress(Exception):
            table_arquivos.find_element(
                By.XPATH,
                el.XPATH_CHECK_CONTAINS_FILES,
            )
            contem_arquivos = False

        if contem_arquivos:
            btn_remove_arquivo = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.CSS_BTN_REMOVE_ARQUIVO,
                )),
            )
            for arquivo in table_arquivos.find_elements(By.TAG_NAME, "tr"):
                tds = arquivo.find_elements(By.TAG_NAME, "td")
                tds[0].find_element(By.TAG_NAME, "input").click()
                btn_remove_arquivo.click()

                with suppress(Exception):
                    Alert(self.driver).accept()

    def __peticao_principal(self) -> None:
        """Empty."""
        bot_data = self.bot_data
        self.print_msg(
            message="Enviando petição principal.",
            type_log="log",
            row=self.row,
        )

        nome_arquivo = bot_data["PETICAO_PRINCIPAL"]
        tipo_arquivo = bot_data["TIPO_ARQUIVO"]
        self.__envia_arquivo(
            nome_arquivo=nome_arquivo,
            tipo_arquivo=tipo_arquivo,
            peticao_principal=True,
        )

        self.print_msg(
            message="Petição principal enviada!",
            type_log="info",
            row=self.row,
        )

    def __anexos_adicionais(self) -> None:
        """Empty."""
        self.print_msg(
            message="Enviando anexos...",
            type_log="log",
            row=self.row,
        )
        bot_data = self.bot_data
        anexos_data = bot_data["ANEXOS"]
        tipo_anexos_data = bot_data["TIPO_ANEXOS"]
        anexos = anexos_data.split(",") if "," in anexos_data else [anexos_data]
        tipo_anexos = (
            tipo_anexos_data.split(",")
            if "," in tipo_anexos_data
            else [tipo_anexos_data]
        )

        for pos, nome_arquivo in enumerate(anexos):
            self.print_msg(
                message=f'Enviando anexo "{nome_arquivo}"',
                type_log="log",
                row=self.row,
            )
            tipo_arquivo = tipo_anexos[pos]
            self.__envia_arquivo(
                nome_arquivo=nome_arquivo,
                tipo_arquivo=tipo_arquivo,
            )
            self.print_msg(
                message="Anexo enviado!",
                type_log="info",
                row=self.row,
            )

    def __envia_arquivo(
        self,
        nome_arquivo: str,
        tipo_arquivo: str,
        *,
        peticao_principal: bool = False,
    ) -> None:
        """Realiza o envio de um arquivo para o sistema Projudi e seleciona seu tipo.

        Args:
            nome_arquivo (str): Nome do arquivo a ser enviado.
            tipo_arquivo (str): Tipo do arquivo a ser selecionado.
            peticao_principal (bool): Indica se é petição principal.

        Raises:
            FileError: Caso o arquivo não seja encontrado após upload.

        """
        out = self.output_dir_path
        nome_arq_normalizado = format_string(nome_arquivo)
        path_arq = out.joinpath(nome_arq_normalizado)

        wait = WebDriverWait(self.driver, 10)
        input_file: WebElementBot = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_INPUT_ARQUIVO,
            )),
        )

        input_file.send_file(path_arq)
        sleep(0.5)
        self.__wait_upload_file()

        table_arquivos = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_TABLE_ARQUIVOS,
            )),
        )

        files = list(table_arquivos.find_elements(By.TAG_NAME, "tr"))
        _files_name = [
            f.find_elements(By.TAG_NAME, "td")[1]
            .find_element(By.TAG_NAME, "a")
            .text
            for f in files
        ]

        tr_arquivo = list(
            filter(
                lambda x: x.find_elements(By.TAG_NAME, "td")[1]
                .find_element(By.TAG_NAME, "a")
                .text
                == nome_arq_normalizado,
                files,
            ),
        )

        if not tr_arquivo:
            raise FileError(
                message=f'Falha ao enviar arquivo "{nome_arquivo}"',
            )

        self.__seleciona_tipo_arquivo(
            tr_arquivo=tr_arquivo[-1],
            tipo_arquivo=tipo_arquivo,
            peticao_principal=peticao_principal,
        )

    def __seleciona_tipo_arquivo(
        self,
        tr_arquivo: WebElementBot,
        tipo_arquivo: str,
        *,
        peticao_principal: bool = False,
    ) -> None:
        wait = WebDriverWait(self.driver, 10)
        tds = tr_arquivo.find_elements(By.TAG_NAME, "td")
        if peticao_principal:
            radio_arq = tds[0].find_element(By.TAG_NAME, "input")
            radio_arq.click()

        select_tipo_arquivos = tds[2].find_element(By.TAG_NAME, "select")
        select = Select(select_tipo_arquivos)

        options_filter = list(
            filter(
                lambda x: x.text == tipo_arquivo,
                select_tipo_arquivos.find_elements(By.TAG_NAME, "option"),
            ),
        )

        if not options_filter:
            options_filter = [
                select_tipo_arquivos.find_element(
                    By.CSS_SELECTOR,
                    'option[value="1"]',
                ),
            ]

        value_option = options_filter[-1].get_attribute("value")

        select.select_by_value(value_option)

        if value_option == "1":
            campo_input_outros = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="descricoes"]',
                )),
            )
            campo_input_outros.send_keys(tipo_arquivo)

    def __assinar(self) -> None:
        wait = WebDriverWait(self.driver, 10)
        senha_token = self.token

        input_senha_token = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_SENHA_CERTIFICADO,
            )),
        )
        input_senha_token.send_keys(senha_token)
        senha_incorreta = False
        input_senha_token.send_keys(Keys.ENTER)

        with suppress(Exception):
            WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[id="errorMessages"]',
                )),
            )
            senha_incorreta = True

        if senha_incorreta:
            raise_password_token()

    def __confirma_protocolo(self) -> str | None:
        with suppress(TimeoutException):
            return (
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "#successMessages",
                    )),
                )
                .text.split("Protocolo:")[1]
                .replace(" ", "")
            )

    def __finaliza_peticionamento(self) -> None:
        message = f"Concluindo peticionamento do processo {self.bot_data.get('NUMERO_PROCESSO')}"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        finish_button = self.driver.find_element(
            By.CSS_SELECTOR,
            el.CSS_BTN_CONCLUIR_MOVIMENTO,
        )
        finish_button.click()

    def __screenshot_sucesso(self) -> DataSucesso:
        """Capture and merge screenshots after successful protocol processing.

        Returns:
            DataSucesso: DataSucesso

        """
        pid = self.pid

        out_dir = self.output_dir_path
        bot_data = self.bot_data
        numero_processo = bot_data["NUMERO_PROCESSO"]

        comprovante1_name = f"COMPROVANTE - {numero_processo} - {pid}.png"
        path_comprovante1 = out_dir.joinpath(comprovante1_name)

        comprovante2_name = f"Protocolo - {numero_processo} - {pid}.png"
        path_comprovante2 = out_dir.joinpath(comprovante2_name)

        file_screenshot_0 = self.output_dir_path.joinpath("tr_0.png")
        file_screenshot_1 = self.output_dir_path.joinpath("tr_1.png")

        table_moves = self.driver.find_element(By.CLASS_NAME, "resultTable")
        table_moves = table_moves.find_elements(By.XPATH, el.table_mov)

        with file_screenshot_0.open("wb") as fp:
            fp.write(table_moves[0].screenshot_as_png)

        expand = table_moves[0].find_element(
            By.CSS_SELECTOR,
            el.expand_btn_projudi,
        )
        expand.click()

        sleep(1.5)

        with file_screenshot_1.open("wb") as fp:
            fp.write(table_moves[1].screenshot_as_png)

        im_tr1 = Image.open(file_screenshot_0)
        im_tr2 = Image.open(file_screenshot_1)

        # Obtenha as dimensões das imagens
        width1, height1 = im_tr1.size
        width2, height2 = im_tr2.size

        # Calcule a largura e altura total para combinar as imagens
        total_height = height1 + height2
        total_width = max(width1, width2)

        # Crie uma nova imagem com o tamanho combinado
        combined_image = Image.new("RGB", (total_width, total_height))

        # Cole as duas imagens (uma em cima da outra)
        combined_image.paste(im_tr1, (0, 0))
        combined_image.paste(im_tr2, (0, height1))

        # Salve a imagem combinada

        with path_comprovante1.open("wb") as fp:
            combined_image.save(fp)

        with path_comprovante2.open("wb") as fp:
            fp.write(self.driver.get_screenshot_as_png())

        message = f"Peticionamento do processo Nº{self.bot_data.get('NUMERO_PROCESSO')} concluído com sucesso!"
        type_log = "success"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        return DataSucesso(
            NUMERO_PROCESSO=numero_processo,
            MENSAGEM=message,
            NOME_COMPROVANTE=comprovante1_name,
            NOME_COMPROVANTE_2=comprovante2_name,
        )

    def __wait_upload_file(self) -> None:
        while True:
            sleep(0.5)
            try:
                progress_bar = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'div[id="divProgressBarContainerAssinado"]',
                )
                style_progressbar = progress_bar.get_attribute("style")

                if style_progressbar == "visibility: hidden;":
                    break
            except Exception:
                break

    def __confirma_inclusao(self) -> None:
        wait = WebDriverWait(self.driver, 10)

        btn_confirma_inclusao = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_BTN_CONFIRMA_INCLUSAO,
            )),
        )

        btn_confirma_inclusao.click()
