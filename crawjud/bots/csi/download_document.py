"""Download de anexos de chamados do CSI."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, TypeVar

import httpx
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from crawjud.controllers.csi import CsiBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls
from crawjud.resources.elements import csi as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot

load_dotenv()

T = TypeVar("TDownloadDocumento", bound=Any)


@shared_task(name="csi.download_documento", bind=True, base=ContextTask)
@wrap_cls
class DownloadDocumento(CsiBot):
    """Robô de download de documentos do CSI."""

    def execution(
        self,
        *args: T,
        **kwargs: T,
    ) -> None:
        tqdm.write("OK")

        frame = self.frame
        self.driver.maximize_window()
        self.total_rows = len(frame)

        for pos, item in enumerate(frame):
            if self.event_stop_bot.is_set():
                break

            self.bot_data = item
            self.row = pos + 1
            self.queue()

        self.driver.quit()

    def queue(self) -> None:
        try:
            self.busca_chamado()

            message = "Chamado encontrado!"
            type_log = "info"
            self.print_msg(message=message, type_log=type_log, row=self.row)
            self.download_anexos_chamado()

        except Exception as e:
            self.append_error(exc=e)

    def busca_chamado(self) -> WebElementBot:
        numero_chamado = self.bot_data["NUMERO_CHAMADO"]

        message = f"Buscando chamado pelo n.{numero_chamado}"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

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
            ec.presence_of_element_located((By.XPATH, el.XPATH_BTN_BUSCAR)),
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
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        wait = WebDriverWait(self.driver, 10)
        self.swtich_iframe_anexos(wait)

        cookies = {
            item["name"]: item["value"] for item in self.driver.get_cookies()
        }

        out_dir = self.output_dir_path
        chamado = self.bot_data["NUMERO_CHAMADO"]

        anexos = wait.until(
            ec.presence_of_element_located((By.TAG_NAME, "tbody")),
        ).find_elements(By.TAG_NAME, "tr")[1:]

        with httpx.Client(cookies=cookies) as client:
            for anexo in anexos:
                if self.event_stop_bot.is_set():
                    break

                with suppress(Exception):
                    anexo.scroll_to()

                td_anexo = anexo.find_elements(By.TAG_NAME, "td")[0]
                anexo_info = td_anexo.find_element(By.TAG_NAME, "a")

                nome_anexo = f"{self.pid} - {chamado} - {anexo_info.text}"
                path_anexo = out_dir.joinpath(nome_anexo)
                link_anexo = anexo_info.get_attribute("href")

                message = f"Baixando arquivo {anexo_info.text}"
                type_log = "log"
                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
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
                type_log = "info"
                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
                )

        self.driver.switch_to.default_content()

        message = "Anexos Baixados com sucesso!"
        type_log = "success"
        self.print_msg(message=message, type_log=type_log, row=self.row)

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
