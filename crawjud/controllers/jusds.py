"""Módulo para a classe de controle dos robôs Jusds."""

from __future__ import annotations

import platform
from contextlib import suppress
from pathlib import Path
from time import perf_counter, sleep
from typing import TYPE_CHECKING, TypeVar

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import raise_start_error
from crawjud.controllers.main import CrawJUD
from crawjud.interfaces.types.bots import DataSucesso
from crawjud.resources.elements import jusds as el

if TYPE_CHECKING:
    from crawjud.custom.task import ContextTask

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15

T_JusdsBot = TypeVar("JusdsBot")


class JusdsBot(CrawJUD):
    """Classe de controle para robôs do Jusds."""

    def __init__(
        self,
        current_task: ContextTask = None,
        storage_folder_name: str | None = None,
        name: str | None = None,
        system: str | None = None,
        *args: T_JusdsBot,
        **kwargs: T_JusdsBot,
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
        link = el.URL_LOGIN_JUSDS

        self.main_window = self.driver.current_window_handle

        wait = WebDriverWait(self.driver, 15)

        self.driver.get(url=link)

        campo_login = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_CAMPO_INPUT_LOGIN,
            )),
        )
        campo_senha = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_CAMPO_INPUT_SENHA,
            )),
        )

        btn_entrar = wait.until(
            ec.presence_of_element_located((By.XPATH, el.XPATH_BTN_ENTRAR)),
        )

        campo_login.send_keys(self.username)
        campo_senha.send_keys(self.password)

        btn_entrar.click()

        with suppress(Exception):
            wait.until(ec.url_to_be(el.URL_CONFIRMA_LOGIN))
            return True

        return False

    def search(self) -> bool:
        """Busca processos no JUSDS.

        Returns:
            bool: Boleano da busca processual

        """
        if not self.window_busca_processo:
            self.driver.switch_to.window("window")
            self.window_busca_processo = self.driver.current_window_handle

            self.driver.get(el.LINK_CONSULTA_PROCESSO)

        elif self.window_busca_processo:
            self.driver.switch_to.window(self.window_busca_processo)

        numero_processo = self.bot_data["NUMERO_PROCESSO"]
        wait = WebDriverWait(self.driver, 15)

        wait_select = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_SELECT_CAMPO_BUSCA,
            )),
        )

        select = Select(wait_select)
        select.select_by_value("1")

        campo_busca_processo = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.CSS_CAMPO_BUSCA_PROCESSO,
            )),
        )

        campo_busca_processo.send_keys(numero_processo)

        with suppress(Exception):
            wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    el.XPATH_BTN_ENTRA_PROCESSO,
                )),
            )

            btn_entra_processo = wait.until(
                ec.element_to_be_clickable((
                    By.XPATH,
                    el.XPATH_BTN_ENTRA_PROCESSO,
                )),
            )

            btn_entra_processo.click()

            window = list(
                filter(
                    lambda x: x != self.window_busca_processo
                    and x != self.main_window,
                    self.driver.window_handles,
                ),
            )

            self.driver.switch_to.window(window[-1])

            args_url = self.driver.current_url.split("form.jsp?")[1]

            self.driver.close()

            self.driver.switch_to.window(self.window_busca_processo)

            self.driver.get(
                el.URL_INFORMACOES_PROCESSO.format(args_url=args_url),
            )

            return True

        return False

    def print_comprovante(self, message: str) -> None:
        numero_processo = self.bot_data.get("NUMERO_PROCESSO")
        name_comprovante = f"Comprovante - {numero_processo} - {self.pid}.png"
        savecomprovante = self.output_dir_path.joinpath(name_comprovante)

        with savecomprovante.open("wb") as fp:
            fp.write(self.driver.get_screenshot_as_png())

        data = DataSucesso(
            NUMERO_PROCESSO=numero_processo,
            MENSAGEM=message,
            NOME_COMPROVANTE=name_comprovante,
            NOME_COMPROVANTE_2="",
        )
        self.append_success(data=data)

        self.print_msg(message=message, type_log="success", row=self.row)
