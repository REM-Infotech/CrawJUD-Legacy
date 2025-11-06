"""Módulo para a classe de controle dos robôs Jusds."""

from contextlib import suppress

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from app.bots.head import CrawJUD
from app.bots.resources.elements import jusds as el
from app.interfaces import DataSucesso


class JusdsBot(CrawJUD):
    """Classe de controle para robôs do Jusds."""

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
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_ENTRAR,
            )),
        )

        campo_login.send_keys(self.credenciais.username)
        campo_senha.send_keys(self.credenciais.password)

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
        message = f"Buscando processo {self.bot_data['NUMERO_PROCESSO']}"
        message_type = "log"

        self.print_message(
            message=message,
            message_type=message_type,
        )

        if not self.window_busca_processo:
            not_mainwindow = list(
                filter(
                    lambda x: x != self.main_window,
                    self.driver.window_handles,
                ),
            )

            if not_mainwindow:
                self.driver.switch_to.window(not_mainwindow[0])
                self.window_busca_processo = self.driver.current_window_handle

        elif self.window_busca_processo:
            self.driver.switch_to.window(self.window_busca_processo)

        self.driver.get(el.LINK_CONSULTA_PROCESSO)

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
                By.CSS_SELECTOR,
                el.CSS_CAMPO_BUSCA_PROCESSO,
            )),
        )

        campo_busca_processo.send_keys(numero_processo)

        btn_buscar = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_BUSCAR_PROCESSO,
            )),
        )

        btn_buscar.click()

        with suppress(Exception):
            wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    el.XPATH_BTN_ENTRA_PROCESSO,
                )),
            )

            with suppress(Exception):
                modal_load = wait.until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        el.XPATH_LOAD_MODAL,
                    )),
                )

                if modal_load:
                    btn_close_modal = wait.until(
                        ec.presence_of_element_located((
                            By.XPATH,
                            el.XPATH_CLOSE_MODAL,
                        )),
                    )
                    btn_close_modal.click()

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
            message = "Processo encontrado!"
            message_type = "info"
            self.print_message(
                message=message,
                message_type=message_type,
            )
            return True

        message = "Processo não encontrado!"
        message_type = "error"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        return False

    def print_comprovante(self, message: str) -> None:
        numero_processo = self.bot_data.get("NUMERO_PROCESSO")
        name_comprovante = f"Comprovante - {numero_processo} - {self.pid}.png"
        savecomprovante = self.output_dir_path.joinpath(
            name_comprovante,
        )

        with savecomprovante.open("wb") as fp:
            fp.write(self.driver.get_screenshot_as_png())

        data = DataSucesso(
            NUMERO_PROCESSO=numero_processo,
            MENSAGEM=message,
            NOME_COMPROVANTE=name_comprovante,
            NOME_COMPROVANTE_2="",
        )
        self.append_success(data=data)

        self.print_message(
            message=message,
            message_type="success",
        )

    def exit_iframe(self) -> None:
        if ".jsp" in self.driver.current_url:
            url = self.driver.current_url.split(".jsp?")[1]

            link_prazos = el.URL_CORRETA.format(url=url)

            self.driver.get(url=link_prazos)

        else:
            self.driver.refresh()
