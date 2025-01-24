import os
import pathlib
import platform
import string
import subprocess
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from ..shared import PropertiesCrawJUD

if platform.system() == "Windows":
    from pywinauto import Application


class AuthBot(PropertiesCrawJUD):

    @classmethod
    def auth(cls) -> bool:

        to_call = getattr(AuthBot, f"{cls.system.lower()}_auth")
        if to_call:
            return to_call()

        raise RuntimeError("Sistema Não encontrado!")

    @classmethod
    def esaj_auth(cls):

        try:
            loginuser = "".join(
                filter(lambda x: x not in string.punctuation, cls.username)
            )
            passuser = cls.password
            if cls.login_method == "cert":

                cls.driver.get(cls.elements.url_login_cert)
                sleep(3)
                loginopt: WebElement = cls.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'select[id="certificados"]')
                    )
                )
                loginopt = loginopt.find_elements(By.TAG_NAME, "option")

                item = None

                try:
                    item = next(
                        filter(lambda item: loginuser in item.text, loginopt), None
                    )

                except Exception as e:
                    raise e
                if item:
                    try:

                        sencert = item.get_attribute("value")
                        select = Select(
                            cls.driver.find_element(
                                By.CSS_SELECTOR, 'select[id="certificados"]'
                            )
                        )
                        select.select_by_value(sencert)
                        entrar = cls.driver.find_element(
                            By.XPATH, '//*[@id="submitCertificado"]'
                        )
                        entrar.click()
                        sleep(2)

                        user_accept_cert_dir = os.path.join(
                            cls.path_accepted, "ACCEPTED"
                        )
                        if not os.path.exists(user_accept_cert_dir):
                            cls.accept_cert(user_accept_cert_dir)

                    except Exception as e:
                        raise e

                elif not item:
                    return False

                checkloged = None
                with suppress(TimeoutException):

                    checkloged = WebDriverWait(cls.driver, 15).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "#esajConteudoHome > table:nth-child(4) > tbody > tr > td.esajCelulaDescricaoServicos",
                            )
                        )
                    )

                if not checkloged:
                    return False

                return True

            cls.driver.get(cls.elements.url_login)
            sleep(3)

            userlogin = cls.driver.find_element(
                By.CSS_SELECTOR, cls.elements.campo_username
            )
            userlogin.click()
            userlogin.send_keys(loginuser)

            userpass = cls.driver.find_element(
                By.CSS_SELECTOR, cls.elements.campo_passwd
            )
            userpass.click()
            userpass.send_keys(passuser)
            entrar = cls.driver.find_element(By.CSS_SELECTOR, cls.elements.btn_entrar)
            entrar.click()
            sleep(2)

            checkloged = None
            with suppress(TimeoutException):

                checkloged = WebDriverWait(cls.driver, 15).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            cls.elements.chk_login,
                        )
                    )
                )

            return checkloged is not None

        except Exception as e:
            raise e

    @classmethod
    def projudi_auth(cls) -> None:

        try:
            cls.driver.get(cls.elements.url_login)

            username: WebElement = cls.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, cls.elements.campo_username)
                )
            )
            username.send_keys(cls.username)

            password = cls.driver.find_element(
                By.CSS_SELECTOR, cls.elements.campo_passwd
            )
            password.send_keys(cls.password)

            entrar = cls.driver.find_element(By.CSS_SELECTOR, cls.elements.btn_entrar)
            entrar.click()

            check_login = None

            with suppress(TimeoutException):
                check_login = WebDriverWait(cls.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, cls.elements.chk_login)
                    )
                )

            return check_login is not None

        except Exception as e:
            raise e

    @classmethod
    def elaw_auth(cls) -> bool:

        try:
            cls.driver.get("https://amazonas.elaw.com.br/login")

            # wait until page load
            username: WebElement = cls.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username.send_keys(cls.username)

            password: WebElement = cls.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
            )
            password.send_keys(cls.password)

            entrar: WebElement = cls.wait.until(
                EC.presence_of_element_located((By.ID, "j_id_a_1_5_f"))
            )
            entrar.click()

            sleep(7)

            url = cls.driver.current_url
            return url != "https://amazonas.elaw.com.br/login"

        except Exception as e:
            raise e

    @classmethod
    def pje_auth(cls):

        try:
            cls.driver.get(cls.elements.url_login)

            login = cls.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, cls.elements.login_input)
                )
            )
            password = cls.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, cls.elements.password_input)
                )
            )
            entrar = cls.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, cls.elements.btn_entrar)
                )
            )

            login.send_keys(cls.username)
            sleep(0.5)
            password.send_keys(cls.password)
            sleep(0.5)
            entrar.click()

            logado = None
            with suppress(TimeoutException):
                logado = cls.wait.until(EC.url_to_be(cls.elements.chk_login))

            return logado is not None

        except Exception as e:
            raise e

    @classmethod
    def accept_cert(cls, accepted_dir: str):

        try:

            path = r"C:\Users\%USERNAME%\AppData\Local\Softplan Sistemas\Web Signer"
            resolved_path = os.path.expandvars(path)

            app = Application(backend="uia").connect(
                path=resolved_path, cache_enable=True
            )
            janela_principal = app.window()
            janela_principal.set_focus()
            button = janela_principal.descendants(control_type="Button")
            checkbox = janela_principal.descendants(control_type="CheckBox")

            sleep(0.5)

            checkbox[0].click_input()
            sleep(0.5)
            button[1].click_input()

            target_directory = os.path.join(
                pathlib.Path(accepted_dir).parent.resolve(), "chrome"
            )
            os.makedirs(target_directory, exist_ok=True, mode=0o775)
            source_directory = cls.chr_dir

            try:

                comando = [
                    "xcopy",
                    source_directory,
                    target_directory,
                    "/E",
                    "/H",
                    "/C",
                    "/I",
                ]
                resultados = subprocess.run(
                    comando,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print(resultados.stdout)

            except Exception as e:
                raise e

            with open(accepted_dir.encode("utf-8"), "w") as f:
                f.write("")

        except Exception as e:
            raise e
