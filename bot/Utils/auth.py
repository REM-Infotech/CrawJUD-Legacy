"""Module: auth.

This module provides the AuthBot class for handling authentication across different systems.

Classes:
    AuthBot: A class for handling authentication across different systems.
"""

import logging
import os
import platform
import string
import subprocess  # nosec: B404 # noqa: S404
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Callable

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import Select, WebDriverWait

from ..core import CrawJUD

if platform.system() == "Windows":
    from ..core import Application

logger = logging.getLogger(__name__)


class AuthBot(CrawJUD):
    """AuthBot class for handling authentication across different systems.

    Methods
    -------
    __init__() -> None
        Initializes the AuthBot instance.
    auth() -> bool:
        Determines the appropriate authentication method based on the system and calls it.
    esaj_auth() -> bool:
        Handles authentication for the ESAJ system.
    projudi_auth() -> bool:
        Handles authentication for the Projudi system.
    elaw_auth() -> bool:
        Handles authentication for the eLaw system.
    pje_auth() -> bool:
        Handles authentication for the PJE system.
    accept_cert(accepted_dir: str) -> None:
        Accepts the certificate for the user.

    """

    def __init__(self) -> None:
        """Initialize the AuthBot instance.

        Initializes the AuthBot with necessary attributes and configurations.
        """
        # Initialize any additional attributes here

    def auth(self) -> bool:
        """Authenticate the user based on the system attribute.

        This method dynamically calls the appropriate authentication method
        for the system specified in the `self.system` attribute. The method
        name is constructed by converting the system name to lowercase and
        appending '_auth'. If the method exists, it is called and its result
        is returned. If the method does not exist, a RuntimeError is raised.

        Returns:
            bool: The result of the authentication method.

        Raises:
            RuntimeError: If the authentication method for the specified system is not found.

        """
        to_call: Callable[[], bool] = getattr(AuthBot, f"{self.system.lower()}_auth", None)
        if to_call:
            return to_call(self)

        raise RuntimeError("Sistema Não encontrado!")

    def esaj_auth(self) -> bool:
        """Authenticate the user on the ESAJ system.

        This method handles both certificate-based and username/password-based
        authentication methods. It navigates to the appropriate login page,
        fills in the required fields, and submits the login form.

        Returns:
            bool: True if authentication is successful, False otherwise.

        """
        try:
            loginuser = "".join(filter(lambda x: x not in string.punctuation, self.username))
            passuser = self.password
            if self.login_method == "cert":
                self.driver.get(self.elements.url_login_cert)
                sleep(3)
                loginopt: WebElement = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'select[id="certificados"]')),
                )
                loginopt = loginopt.find_elements(By.TAG_NAME, "option")

                item = None

                try:
                    item = next(filter(lambda item: loginuser in item.text, loginopt), None)

                except Exception as e:
                    raise e
                if item:
                    try:
                        sencert = item.get_attribute("value")
                        select = Select(self.driver.find_element(By.CSS_SELECTOR, 'select[id="certificados"]'))
                        select.select_by_value(sencert)
                        entrar = self.driver.find_element(By.XPATH, '//*[@id="submitCertificado"]')
                        entrar.click()
                        sleep(2)

                        user_accept_cert_dir = os.path.join(self.path_accepted, "ACCEPTED")
                        if not os.path.exists(user_accept_cert_dir):
                            self.accept_cert(user_accept_cert_dir)

                    except Exception as e:
                        raise e

                elif not item:
                    return False

                checkloged = None
                with suppress(TimeoutException):
                    checkloged = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "#esajConteudoHome > table:nth-child(4) > tbody > tr > td.esajCelulaDescricaoServicos",
                            ),
                        ),
                    )

                if not checkloged:
                    return False

                return True

            self.driver.get(self.elements.url_login)
            sleep(3)

            userlogin = self.driver.find_element(By.CSS_SELECTOR, self.elements.campo_username)
            userlogin.click()
            userlogin.send_keys(loginuser)

            userpass = self.driver.find_element(By.CSS_SELECTOR, self.elements.campo_passwd)
            userpass.click()
            userpass.send_keys(passuser)
            entrar = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_entrar)
            entrar.click()
            sleep(2)

            checkloged = None
            with suppress(TimeoutException):
                checkloged = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.chk_login)),
                )

            return checkloged is not None

        except Exception as e:
            raise e

    def projudi_auth(self) -> bool:
        """Authenticate the user on the Projudi platform.

        This method navigates to the login page, enters the username and password,
        and attempts to log in. It then checks if the login was successful.

        Returns:
            bool: True if login was successful, False otherwise.


        """
        try:
            self.driver.get(self.elements.url_login)

            username: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.campo_username)),
            )
            username.send_keys(self.username)

            password = self.driver.find_element(By.CSS_SELECTOR, self.elements.campo_passwd)
            password.send_keys(self.password)

            entrar = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_entrar)
            entrar.click()

            check_login = None

            with suppress(TimeoutException):
                check_login = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.chk_login)),
                )

            return check_login is not None

        except Exception as e:
            raise e

    def elaw_auth(self) -> bool:
        """Authenticate the user on the eLaw platform.

        This method navigates to the eLaw login page, enters the username and password,
        and attempts to log in. It waits for the necessary elements to be present on the page
        before interacting with them. After attempting to log in, it checks the current URL
        to determine if the login was successful.

        Returns:
            bool: True if the login was successful, False otherwise.

        """
        try:
            self.driver.get("https://amazonas.elaw.com.br/login")

            # wait until page load
            username: WebElement = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username.send_keys(self.username)

            password: WebElement = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#password")))
            password.send_keys(self.password)

            entrar: WebElement = self.wait.until(EC.presence_of_element_located((By.ID, "j_id_a_1_5_f")))
            entrar.click()

            sleep(7)

            url = self.driver.current_url
            return url != "https://amazonas.elaw.com.br/login"

        except Exception as e:
            raise e

    def pje_auth(self) -> bool:
        """Authenticate the user on the PJE system.

        This method navigates to the login page, inputs the username and password,
        and attempts to log in. It waits for the login elements to be present on the page,
        sends the credentials, and clicks the login button. Finally, it checks if the login
        was successful by verifying the URL.

        Returns:
            bool: True if login was successful, False otherwise.


        """
        try:
            self.driver.get(self.elements.url_login)

            login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.login_input)))
            password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.password_input)))
            entrar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.btn_entrar)))

            login.send_keys(self.username)
            sleep(0.5)
            password.send_keys(self.password)
            sleep(0.5)
            entrar.click()

            logado = None
            with suppress(TimeoutException):
                logado = WebDriverWait(self.driver, 10).until(EC.url_to_be(self.elements.chk_login))

            return logado is not None

        except Exception as e:
            raise e

    def accept_cert(self, accepted_dir: str) -> None:
        """Accept the certificate for the user.

        This method automates the acceptance of certificates by interacting with
        the certificate management application. It copies necessary files and ensures
        that the certificate is properly accepted.

        Args:
            accepted_dir (str): The directory where accepted certificates are stored.


        """
        try:
            path = r"C:\Users\%USERNAME%\AppData\Local\Softplan Sistemas\Web Signer"
            resolved_path = os.path.expandvars(path)

            app = Application(backend="uia").connect(path=resolved_path, cache_enable=True)
            janela_principal = app.window()
            janela_principal.set_focus()
            button = janela_principal.descendants(control_type="Button")
            checkbox = janela_principal.descendants(control_type="CheckBox")

            sleep(0.5)

            checkbox[0].click_input()
            sleep(0.5)
            button[1].click_input()

            target_directory = Path(accepted_dir).parent.joinpath("chrome").resolve()

            target_directory.mkdir(exist_ok=True)
            source_directory = self.chr_dir

            try:
                comando = ["xcopy", source_directory, target_directory, "/E", "/H", "/C", "/I"]
                resultados = subprocess.run(  # noqa: S603 # nosec: B603
                    comando,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                logger.info(str(resultados.stdout))

            except Exception as e:
                raise e

            with open(Path(accepted_dir), "w", encoding="utf-8") as f:  # noqa: FURB103
                f.write("")

        except Exception as e:
            raise e
