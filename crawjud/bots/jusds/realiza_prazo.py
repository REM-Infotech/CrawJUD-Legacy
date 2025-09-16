"""empty."""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.jusds import JusdsBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import jusds as el

if TYPE_CHECKING:
    from collections.abc import Generator

    from crawjud.utils.webdriver.web_element import WebElementBot


@shared_task(name="jusds.realiza_prazo", bind=True, context=ContextTask)
@wrap_cls
class RealizaPrazos(JusdsBot):
    """empty."""

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        window = list(
            filter(
                lambda x: x != self.main_window,
                self.driver.window_handles,
            ),
        )

        if window:
            self.driver.switch_to.window(window[-1])

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        bot_data = self.bot_data

        try:
            numero_prazo = bot_data["NUMERO_COMPROMISSO"]

            message = f"Buscando prazo com o ID {numero_prazo}"
            type_log = "log"

            self.print_msg(message=message, type_log=type_log, row=self.row)

            for pos, prazo in enumerate(self.iter_prazos()):
                td_prazo = prazo.find_elements(By.TAG_NAME, "td")

                self.print_msg(
                    message=str(pos),
                    type_log=type_log,
                    row=self.row,
                )

                sleep(0.5)

                prazo_numero_jusds = td_prazo[8].text

                if prazo_numero_jusds == str(numero_prazo):
                    tqdm.write("ok")
                    sleep(15)

                    _sit_prazo = td_prazo[6]

                    message = "Prazo encontrado!"
                    type_log = "success"

                    self.print_msg(message=message, type_log=type_log)

                    break

        except (ExecutionError, Exception) as e:
            self.append_error(e)

    def iter_prazos(self) -> Generator[WebElementBot, Any, None]:
        wait = WebDriverWait(self.driver, 10)

        if ".jsp" in self.driver.current_url:
            url = self.driver.current_url.split(".jsp?")[1]

            link_prazos = (
                f"https://infraero.jusds.com.br/JRD/openform.do?{url}"
            )

            self.driver.get(url=link_prazos)

        else:
            self.driver.refresh()

        sleep(5)

        while True:
            btn_next_page = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    el.XPATH_BTN_NEXT_PAGE,
                )),
            )

            table_prazos = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    el.XPATH_TABLE_PRAZOS,
                )),
            ).find_elements(By.TAG_NAME, "tr")

            yield from table_prazos

            if "disabled" in btn_next_page.get_attribute("class"):
                break

            sleep(5)

            btn_next_page.click()
