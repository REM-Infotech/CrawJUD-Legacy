"""Download de anexos de chamados do CSI."""

from contextlib import suppress

import httpx
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from app.types import AnyType
from bots.controller.csi import CsiBot
from bots.resources.driver.web_element import WebElementBot
from bots.resources.elements import csi as el

load_dotenv()


class DownloadDocumento(CsiBot):
    """Robô de download de documentos do CSI."""

    def execution(self, *args: AnyType, **kwargs: AnyType) -> None:
        tqdm.write("OK")

        frame = self.frame
        self.driver.maximize_window()
        self.total_rows = len(frame)

        for pos, item in enumerate(frame):
            if self.bot_stopped.is_set():
                break

            self.bot_data = item
            self.row = pos + 1
            self.queue()

        self.finalizar_execucao()

    def queue(self) -> None:
        try:
            self.busca_chamado()

            message = "Chamado encontrado!"
            message_type = "info"
            self.print_message(
                message=message,
                message_type=message_type,
            )
            self.download_anexos_chamado()

        except Exception as e:
            message_error = str(e)

            self.print_message(
                message=f"{message_error}.",
                message_type="error",
            )

            self.bot_data.update({"MOTIVO_ERRO": message_error})
            self.append_error(data_save=[self.bot_data])

    def busca_chamado(self) -> WebElementBot:
        numero_chamado = self.bot_data["NUMERO_CHAMADO"]

        message = f"Buscando chamado pelo n.{numero_chamado}"
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        self.driver.get(url=el.URL_BUSCA_CHAMADO)
        wait = WebDriverWait(self.driver, 10)

        input_numero_chamado = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_INPUT_NUMERO_CHAMADO,
            )),
        )

        input_numero_chamado.send_keys(numero_chamado)
        btn_buscar = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_BUSCAR,
            )),
        )
        btn_buscar.click()

        return wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_TABLE_SOLICITACOES,
            )),
        )

    def download_anexos_chamado(self) -> None:
        message = "Baixando anexos..."
        message_type = "log"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        wait = WebDriverWait(self.driver, 10)
        self.swtich_iframe_anexos(wait)

        cookies = {
            item["name"]: item["value"] for item in self.driver.get_cookies()
        }

        out_dir = self.output_dir_path
        chamado = self.bot_data["NUMERO_CHAMADO"]

        with httpx.Client(cookies=cookies) as client:
            for anexo in wait.until(
                ec.presence_of_element_located((By.TAG_NAME, "tbody")),
            ).find_elements(By.TAG_NAME, "tr")[1:]:
                if self.bot_stopped.is_set():
                    break

                with suppress(Exception):
                    anexo.scroll_to()

                td_anexo = anexo.find_elements(By.TAG_NAME, "td")[0]
                anexo_info = td_anexo.find_element(By.TAG_NAME, "a")

                nome_anexo = f"{self.pid} - {chamado} - {anexo_info.text}"
                path_anexo = out_dir.joinpath(nome_anexo)
                link_anexo = anexo_info.get_attribute("href")

                message = f"Baixando arquivo {anexo_info.text}"
                message_type = "log"
                self.print_message(
                    message=message,
                    message_type=message_type,
                )

                with (
                    client.stream(
                        "get",
                        link_anexo,
                        timeout=240,
                    ) as stream,
                    path_anexo.open("wb") as fp,
                ):
                    for chunk in stream.iter_bytes(chunk_size=8192):
                        fp.write(chunk)

                message = "Arquivo baixado com sucesso!"
                message_type = "info"
                self.print_message(
                    message=message,
                    message_type=message_type,
                )

        self.driver.switch_to.default_content()

        message = "Anexos Baixados com sucesso!"
        message_type = "success"
        self.print_message(
            message=message,
            message_type=message_type,
        )

    def swtich_iframe_anexos(self, wait: WebDriverWait) -> None:
        self.driver.execute_script(
            el.COMMAND_ANEXOS.format(
                NUMERO_CHAMADO=self.bot_data["NUMERO_CHAMADO"],
            ),
        )

        wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_DIV_POPUP_ANEXOS,
            )),
        )

        wait.until(
            ec.frame_to_be_available_and_switch_to_it((
                By.XPATH,
                el.XPATH_IFRAME_ANEXOS,
            )),
        )
