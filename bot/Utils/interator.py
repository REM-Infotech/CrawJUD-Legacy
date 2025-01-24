from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bot.common.exceptions import ItemNaoEcontrado

from ..shared import PropertiesCrawJUD


class Interact(PropertiesCrawJUD):

    @classmethod
    def send_key(cls, element: WebElement, word: any) -> None:

        send = None
        for key in dir(Keys):
            if getattr(Keys, key) == word:
                send = ""
                element.send_keys(word)
                break

        if send is None:
            element.click()
            sleep(0.05)
            for c in str(word):
                sleep(0.001)
                element.send_keys(c)

    @classmethod
    def click(cls, element: WebElement) -> None:

        sleep(0.05)
        element.click()
        sleep(0.05)

    @classmethod
    def double_click(cls, element: WebDriver) -> None:

        Action = ActionChains(cls.driver)
        Action.double_click(element).perform()

    @classmethod
    def select_item(cls, elemento: str, text: str) -> bool | Exception:

        itens: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elemento))
        )

        cls.diplay_none(itens)
        sleep(0.5)

        if not text.isupper():
            itens = list(
                filter(
                    lambda item: not item.text.isupper(),
                    itens.find_element(By.CSS_SELECTOR, "ul").find_elements(
                        By.TAG_NAME, "li"
                    ),
                )
            )

        elif text.isupper():
            itens = itens.find_element(By.TAG_NAME, "ul").find_elements(
                By.TAG_NAME, "li"
            )

        item = next(filter(lambda item: text == item.text, itens), None)

        if not item:
            raise ItemNaoEcontrado(message=f'Item "{text}" não encontrado!')

        Action = ActionChains(cls.driver)
        Action.double_click(item).perform()

        return True

    @classmethod
    def clear(cls, element: WebElement) -> None:

        element.click()
        sleep(0.5)
        element.clear()
        sleep(1)

    @classmethod
    def sleep_load(cls, element: str = 'div[id="j_id_3x"]') -> None:

        while True:
            sleep(0.5)
            load = None
            aria_value = None
            with suppress(TimeoutException):
                load: WebElement = WebDriverWait(cls.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, element))
                )

            if load:

                for attributes in ["aria-live", "aria-hidden", "class"]:
                    aria_value = load.get_attribute(attributes)

                    if not aria_value:
                        continue

                    break

                if aria_value is None or any(
                    value == aria_value
                    for value in [
                        "off",
                        "true",
                        "spinner--fullpage spinner--fullpage--show",
                    ]
                ):
                    break

            if not load:
                break

    @classmethod
    def diplay_none(cls, elemento: WebElement):

        while True:

            style = elemento.get_attribute("style")

            if "display: none;" not in style:
                sleep(0.01)
                break

    @classmethod
    def wait_caixa(cls) -> None:

        while True:

            check_wait = None
            with suppress(NoSuchElementException):
                check_wait = cls.driver.find_element(
                    By.CSS_SELECTOR,
                    'div[id="modal:waitContainer"][style="position: absolute; z-index: 100; background-color: inherit; display: none;"]',
                )

            if check_wait:
                break

    @classmethod
    def wait_fileupload(cls) -> None:

        while True:

            sleep(0.05)
            div1 = 'div[class="ui-fileupload-files"]'
            div2 = 'div[class="ui-fileupload-row"]'
            div0 = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:uploadGedEFile"]'
            progress_bar = None

            div0progress_bar = cls.driver.find_element(By.CSS_SELECTOR, div0)
            div1progress_bar = div0progress_bar.find_element(By.CSS_SELECTOR, div1)

            with suppress(NoSuchElementException):
                progress_bar = div1progress_bar.find_element(By.CSS_SELECTOR, div2)

            if progress_bar is None:
                break

    @classmethod
    def scroll_to(cls, element: WebElement):

        Action = ActionChains(cls.driver)
        Action.scroll_to_element(element)
        sleep(0.5)

    @classmethod
    def Select2_ELAW(cls, elementSelect: str, to_Search: str) -> None:

        selector: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elementSelect))
        )

        items = selector.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        elementsSelecting = elementSelect.replace("'", "'")
        if '"' in elementsSelecting:
            elementsSelecting = elementSelect.replace('"', "'")

        for item in items:

            value_item = item.get_attribute("value")
            cms = f"{elementsSelecting} > option[value='{value_item}']"
            text_item = cls.driver.execute_script(f'return $("{cms}").text();')

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_Search.upper())

        if value_opt:

            command = f"$('{elementSelect}').val(['{value_opt}']);"
            command2 = f"$('{elementSelect}').trigger('change');"

            if "'" in elementSelect:
                command = f"$(\"{elementSelect}\").val(['{value_opt}']);"
                command2 = f"$(\"{elementSelect}\").trigger('change');"

            cls.driver.execute_script(command)
            cls.driver.execute_script(command2)
