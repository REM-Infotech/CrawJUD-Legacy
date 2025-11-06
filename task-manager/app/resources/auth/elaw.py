"""Autenticador Elaw."""

from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from app.resources.auth._main import AutenticadorBot


class AutenticadorElaw(AutenticadorBot):
    def __call__(self) -> bool:
        self.driver.get("https://amazonas.elaw.com.br/login")

        # wait until page load
        username = self.wait.until(
            ec.presence_of_element_located((By.ID, "username")),
        )
        username.send_keys(self.credenciais.username)

        password = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                "#authKey",
            )),
        )
        password.send_keys(self.credenciais.password)

        entrar = self.wait.until(
            ec.presence_of_element_located((By.ID, "j_id_c_1_5_f")),
        )
        entrar.click()

        sleep(7)

        url = self.driver.current_url
        return url != "https://amazonas.elaw.com.br/login"
