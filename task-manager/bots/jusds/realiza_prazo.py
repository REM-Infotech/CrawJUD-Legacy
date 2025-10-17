"""empty."""

from contextlib import suppress
from time import sleep

from common.exceptions import ExecutionError
from resources.elements import jusds as el
from resources.web_element import WebElementBot
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from .master import JusdsBot


class RealizaPrazos(JusdsBot):
    """empty."""

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            self.queue()
            tqdm.write("ok")

        self.finalize_execution()

    def queue(self) -> None:
        try:
            buscar = self.search()

            if not buscar:
                return

            tqdm.write("ok")
            self.tratar_prazo()

        except (ExecutionError, Exception) as e:
            self.append_error(e)

    def tratar_prazo(self) -> None:
        bot_data = self.bot_data
        documentos_anexados = False

        id_prazo = self.bot_data["NUMERO_COMPROMISSO"]

        self.print_message(
            message=f"Buscando compromisso pelo id {id_prazo}",
            message_type="log",
        )

        message_prazo_encontrado = False

        while True:
            prazo = self.find_prazo(id_prazo=id_prazo)
            if prazo:
                if not message_prazo_encontrado:
                    self.print_message(
                        message="Compromisso encontrado!",
                        message_type="info",
                    )
                    message_prazo_encontrado = True

                prazo_items = prazo.find_elements(By.TAG_NAME, "td")
                status_prazo = prazo_items[11]
                status_prazo.scroll_to()

                if bot_data.get("ANEXOS") and not documentos_anexados:
                    anexos = (
                        bot_data.get("ANEXOS").split(",")
                        if "," in bot_data.get("ANEXOS")
                        else [bot_data.get("ANEXOS")]
                    )

                    for anexo in anexos:
                        self.anexar_documentos(anexo_nome=anexo)

                    documentos_anexados = True
                    continue

                self.atualizar_status(prazo=prazo)
                break

    def find_prazo(self, id_prazo: str) -> WebElementBot | None:
        wait = WebDriverWait(self.driver, 10)

        btn_pagina_compromissos = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_COMPROMISSOS,
            )),
        )

        btn_pagina_compromissos.click()

        prazos_list: list[WebElementBot] = wait.until(
            ec.presence_of_element_located((By.XPATH, el.XPATH_TABLE_PRAZOS)),
        ).find_elements(By.TAG_NAME, "tr")

        for prazo in prazos_list:
            with suppress(Exception):
                prazo.scroll_to_element()
                prazo.find_elements(By.TAG_NAME, "td")[0].scroll_to()

                id_prazo_jusds = prazo.find_elements(By.TAG_NAME, "td")[1].text
                if id_prazo_jusds == str(id_prazo):
                    return prazo

        return None

    def anexar_documentos(self, anexo_nome: str) -> None:
        wait = WebDriverWait(self.driver, 10)
        bot_data = self.bot_data

        btn_anexos = wait.until(
            ec.presence_of_element_located((By.XPATH, el.XPATH_BTN_ANEXOS)),
        )
        btn_anexos.click()

        btn_add_anexo = wait.until(
            ec.presence_of_element_located((By.XPATH, el.XPATH_BTN_ADD_ANEXO)),
        )

        btn_add_anexo.click()

        wait.until(
            ec.frame_to_be_available_and_switch_to_it((
                By.XPATH,
                el.XPATH_IFRAME_ANEXOS,
            )),
        )

        wait.until(
            ec.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")),
        )

        campo_tipo_anexo: WebElementBot = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_INPUT_TIPO_DOCUMENTO,
            )),
        )
        campo_tipo_anexo.click()
        campo_tipo_anexo.send_keys(bot_data["TIPO_ANEXOS"])

        sleep(0.5)
        campo_tipo_anexo.send_keys(Keys.ENTER)

        btn_anexar_arquivo = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_AENXAR_ARQUIVO,
            )),
        )

        btn_anexar_arquivo.click()

        self.driver.switch_to.default_content()

        wait.until(
            ec.frame_to_be_available_and_switch_to_it((
                By.XPATH,
                el.XPATH_IFRAME_UPLOAD_ANEXO,
            )),
        )

        nome_anexo_normalizado = self.format_string(anexo_nome)
        path_file = self.output_dir_path.joinpath(nome_anexo_normalizado)

        input_file: WebElementBot = wait.until(
            ec.presence_of_element_located((By.XPATH, el.XPATH_INPUT_FILE)),
        )
        input_file.send_file(str(path_file))

        WebDriverWait(self.driver, 30).until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_ENVIAR_ARQUIVO,
            )),
        ).click()

        WebDriverWait(self.driver, 10).until(ec.alert_is_present()).accept()

        self.driver.switch_to.default_content()

        self.driver.execute_script("window.scrollTo(0, 0);")

        sleep(0.5)

        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_CLOSE_MODAL,
            )),
        ).click()

    def atualizar_status(self, prazo: WebElementBot) -> None:
        wait = WebDriverWait(self.driver, 10)
        prazo_items = prazo.find_elements(By.TAG_NAME, "td")
        status_prazo = prazo_items[11]

        status_prazo.double_click()

        select_status = status_prazo.find_element(By.TAG_NAME, "select")
        option_status = list(
            filter(
                lambda x: x.text.lower() == "concluído",
                select_status.find_elements(By.TAG_NAME, "option"),
            ),
        )

        if option_status:
            select_status.select_item(option_status[0].get_attribute("value"))

        btn_salva = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_SALVA_STATUS,
            )),
        )
        btn_salva.click()

        self.print_comprovante("Compromisso salvo com sucesso")
