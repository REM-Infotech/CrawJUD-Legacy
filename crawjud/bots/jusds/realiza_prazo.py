"""empty."""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.jusds import JusdsBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import jusds as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot


@shared_task(name="jusds.realiza_prazo", bind=True, context=ContextTask)
@wrap_cls
class RealizaPrazos(JusdsBot):
    """empty."""

    @property
    def numero_prazo(self) -> str:
        return self.bot_data["NUMERO_COMPROMISSO"]

    @property
    def btn_next_page(self) -> WebElementBot:
        wait = WebDriverWait(self.driver, 10)
        return wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_NEXT_PAGE,
            )),
        )

    @property
    def table_prazos(self) -> list[WebElementBot]:
        wait = WebDriverWait(self.driver, 10)
        return wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_TABLE_PRAZOS,
            )),
        ).find_elements(By.TAG_NAME, "tr")

    @property
    def prazo_filtrado(self) -> list[WebElementBot]:
        prazo_filtrado = []
        for prazo in self.table_prazos:
            td_prazo = prazo.find_elements(By.TAG_NAME, "td")
            prazo_numero_jusds = td_prazo[8].text
            if prazo_numero_jusds == str(self.numero_prazo):
                self.td_prazo = td_prazo
                prazo_filtrado.append(prazo)
                break

        return prazo_filtrado

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
        self.prazo_encontrado = False

        try:
            message = f"Buscando prazo com o ID {self.numero_prazo}"
            type_log = "log"

            self.print_msg(message=message, type_log=type_log, row=self.row)
            self.exit_iframe()

            sleep(5)

            while True:
                if self.prazo_filtrado:
                    self.tratativas_compromisso()

                if any((
                    "disabled" in self.btn_next_page.get_attribute("class"),
                    self.event_stop_bot.is_set(),
                    self.prazo_encontrado,
                )):
                    break

                self.btn_next_page.click()

            if all((
                not self.prazo_encontrado,
                not self.event_stop_bot.is_set(),
            )):
                message = "Prazo não encontrado!"
                type_log = "error"

                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
                )

        except (ExecutionError, Exception) as e:
            self.append_error(e)

    def tratativas_compromisso(self) -> None:
        self.prazo_encontrado = True

        td_prazo = self.td_prazo
        _sit_prazo = td_prazo[6]

        message = "Prazo encontrado!"
        type_log = "success"

        self.print_msg(
            message=message,
            type_log=type_log,
            row=self.row,
        )
