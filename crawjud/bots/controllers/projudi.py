"""Módulo para a classe de controle dos robôs PROJUDI."""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from crawjud.bots.controllers.master import CrawJUD
from crawjud.bots.projudi.resources import elements as el
from crawjud.common.exceptions.bot import ExecutionError, LoginSystemError

if TYPE_CHECKING:
    from selenium.webdriver.common.alert import Alert

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class ProjudiBot[T](CrawJUD):
    """Classe de controle para robôs do PROJUDI."""

    def auth(self) -> bool:
        check_login = None
        try:
            self.driver.get(el.url_login)

            sleep(1.5)

            self.driver.refresh()

            username = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.campo_username,
                )),
            )
            username.send_keys(self.username)

            password = self.driver.find_element(
                By.CSS_SELECTOR,
                el.campo_2_login,
            )
            password.send_keys(self.password)

            entrar = self.driver.find_element(
                By.CSS_SELECTOR,
                el.btn_entrar,
            )
            entrar.click()

            with suppress(TimeoutException):
                check_login = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.chk_login,
                    )),
                )

            alert = None
            with suppress(TimeoutException):
                alert: type[Alert] = WebDriverWait(self.driver, 5).until(
                    ec.alert_is_present(),
                )

            if alert:
                alert.accept()

        except ExecutionError as e:
            raise LoginSystemError(exception=e) from e

        return check_login is not None
