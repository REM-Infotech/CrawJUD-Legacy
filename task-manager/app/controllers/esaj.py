"""Módulo para a classe de controle dos robôs ESaj."""

from __future__ import annotations

import platform
import string
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import perf_counter, sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

from app.common.exceptions.bot import raise_start_error
from app.controllers.main import CrawJUD
from app.resources.elements import esaj as el

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class ESajBot(CrawJUD):
    """Classe de controle para robôs do ESaj."""

    def __init__(
        self,
        current_task: ContextTask = None,
        storage_folder_name: str | None = None,
        name: str | None = None,
        system: str | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        """Instancia a classe."""
        self.botname = name
        self.botsystem = system

        self.folder_storage = storage_folder_name
        self.current_task = current_task
        self.start_time = perf_counter()
        self.pid = str(current_task.request.id)

        selected_browser = "chrome"
        if platform.system() == "Linux":
            selected_browser = "firefox"

        super().__init__(selected_browser=selected_browser, *args, **kwargs)

        for k, v in kwargs.copy().items():
            setattr(self, k, v)

        self.download_files()

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

            raise_start_error("Falha na autenticação.")

        self.print_msg(message="Sucesso na autenticação!", type_log="info")
        self._frame = self.load_data()

        sleep(0.5)
        self.print_msg(message="Execução inicializada!", type_log="info")

    def auth(self) -> bool:
        loginuser = "".join(
            filter(lambda x: x not in string.punctuation, self.username),
        )
        passuser = self.password
        if self.login_method == "cert":
            self.driver.get(el.url_login_cert)
            sleep(3)
            loginopt = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'select[id="certificados"]',
                )),
            )
            loginopt = loginopt.find_elements(By.TAG_NAME, "option")

            item = None

            item = next(
                filter(lambda item: loginuser in item.text, loginopt),
                None,
            )
            if item:
                sencert = item.get_attribute("value")
                select = Select(
                    self.driver.find_element(
                        By.CSS_SELECTOR,
                        'select[id="certificados"]',
                    ),
                )
                select.select_by_value(sencert)
                entrar = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="submitCertificado"]',
                )
                entrar.click()
                sleep(2)

                user_accept_cert_dir = Path(self.path_accepted) / "ACCEPTED"
                if not user_accept_cert_dir.exists():
                    self.accept_cert(user_accept_cert_dir)

            elif not item:
                return False

            checkloged = None
            with suppress(TimeoutException):
                checkloged = WebDriverWait(self.driver, 15).until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            (
                                "#esajConteudoHome > table:nth-child(4)",
                                " > tbody > ",
                                "tr > td.esajCelulaDescricaoServicos",
                            ),
                        ),
                    ),
                )

            return checkloged is not None

        self.driver.get(el.url_login)
        sleep(3)

        userlogin = self.driver.find_element(
            By.CSS_SELECTOR,
            el.campo_username,
        )
        userlogin.click()
        userlogin.send_keys(loginuser)

        userpass = self.driver.find_element(
            By.CSS_SELECTOR,
            el.campo_2_login,
        )
        userpass.click()
        userpass.send_keys(passuser)
        entrar = self.driver.find_element(
            By.CSS_SELECTOR,
            el.btn_entrar,
        )
        entrar.click()
        sleep(2)

        checkloged = None

        try:
            checkloged = WebDriverWait(self.driver, 15).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.chk_login,
                )),
            )
        except TimeoutException:
            return False

        else:
            return checkloged is not None
