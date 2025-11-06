"""Módulo para a classe de controle dos robôs PROJUDI."""

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bots.resources.elements import projudi as el
from common.exceptions import (
    ExecutionError,
    LoginSystemError,
)

if TYPE_CHECKING:
    from selenium.webdriver.common.alert import Alert


class AutenticadorProjudi:
    def __call__(self) -> bool:
        """Autentique usuário no sistema PROJUDI.

        Returns:
            bool: True se login bem-sucedido, False caso contrário.

        Raises:
            LoginSystemError: Se ocorrer erro na autenticação.

        """
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

            password = self.driver.find_element(
                By.CSS_SELECTOR,
                el.campo_2_login,
            )

            entrar = self.driver.find_element(
                By.CSS_SELECTOR,
                el.btn_entrar,
            )

            username.send_keys(self.credenciais.username)
            password.send_keys(self.credenciais.password)
            entrar.click()

            with suppress(TimeoutException):
                check_login = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.chk_login,
                    )),
                )

            alert = None
            with suppress(TimeoutException, Exception):
                alert: type[Alert] = WebDriverWait(
                    self.driver,
                    5,
                ).until(
                    ec.alert_is_present(),
                )

            if alert:
                alert.accept()

        except ExecutionError as e:
            raise LoginSystemError(exception=e) from e

        return check_login is not None
