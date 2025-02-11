"""Utility module for interacting with web elements using Selenium WebDriver.

Provides the Interact class with methods to perform various interactions
such as clicking, sending keys, and selecting items.
"""

from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from bot.common.exceptions import ItemNaoEcontrado

from ..core import CrawJUD


class Interact(CrawJUD):
    """Provides methods to interact with web elements using Selenium WebDriver."""

    def __init__(self) -> None:
        """Initialize the Interact class."""

    def send_key(self, element: WebElement, word: any) -> None:
        """Send a sequence of keys to a web element.

        Args:
            element (WebElement): The web element to send keys to.
            word (any): The keys or text to send to the element.

        """
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

    def click(self, element: WebElement) -> None:
        """Click on a web element with a short delay before and after.

        Args:
            element (WebElement): The web element to click.

        """
        sleep(0.05)
        element.click()
        sleep(0.05)

    def double_click(self, element: WebElement) -> None:
        """Perform a double-click action on a web element.

        Args:
            element (WebElement): The web element to double-click.

        """
        action = ActionChains(self.driver)
        action.double_click(element).perform()

    def select_item(self, elemento: str, text: str) -> bool:
        """Select an item from a dropdown or list based on the provided text.

        Args:
            elemento (str): The CSS selector of the element containing the items.
            text (str): The text of the item to select.

        Returns:
            bool: True if the item was successfully selected.

        Raises:
            ItemNaoEcontrado: If the item with the specified text is not found.

        """
        itens: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, elemento)))

        self.display_none(itens)
        sleep(0.5)

        if not text.isupper():
            itens = list(
                filter(
                    lambda item: not item.text.isupper(),
                    itens.find_element(By.CSS_SELECTOR, "ul").find_elements(By.TAG_NAME, "li"),
                ),
            )

        elif text.isupper():
            itens = itens.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")

        item = next(filter(lambda item: text == item.text, itens), None)

        if not item:
            raise ItemNaoEcontrado(message=f'Item "{text}" não encontrado!')

        action = ActionChains(self.driver)
        action.double_click(item).perform()

        return True

    def clear(self, element: WebElement) -> None:
        """Clear the content of a web element.

        Args:
            element (WebElement): The web element to clear.

        """
        element.click()
        sleep(0.5)
        element.clear()
        sleep(1)

    def sleep_load(self, element: str = 'div[id="j_id_3x"]') -> None:
        """Wait until a specific element is no longer loading.

        Args:
            element (str, optional): The CSS selector of the loading element.
                                      Defaults to 'div[id="j_id_3x"]'.

        """
        while True:
            sleep(0.5)
            load = None
            aria_value = None
            with suppress(TimeoutException):
                load: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, element)),
                )

            if load:
                for attributes in ["aria-live", "aria-hidden", "class"]:
                    aria_value = load.get_attribute(attributes)

                    if not aria_value:
                        continue

                    break

                if aria_value is None or any(
                    value == aria_value for value in ["off", "true", "spinner--fullpage spinner--fullpage--show"]
                ):
                    break

            if not load:
                break

    def display_none(self, elemento: WebElement) -> None:
        """Wait until the display style of an element is set to 'none'.

        Args:
            elemento (WebElement): The web element to check.

        """
        while True:
            style = elemento.get_attribute("style")

            if "display: none;" not in style:
                sleep(0.01)
                break

    def wait_caixa(self) -> None:
        """Wait until a specific modal dialog is present on the page."""
        while True:
            check_wait = None
            with suppress(NoSuchElementException):
                check_wait = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'div[id="modal:waitContainer"][style="position: absolute; z-index: 100; background-color: inherit; display: none;"]',  # noqa: E501
                )

            if check_wait:
                break

    def wait_fileupload(self) -> None:
        """Wait until the file upload process is complete."""
        while True:
            sleep(0.05)
            div1 = 'div[class="ui-fileupload-files"]'
            div2 = 'div[class="ui-fileupload-row"]'
            div0 = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:uploadGedEFile"]'
            progress_bar = None

            div0progress_bar = self.driver.find_element(By.CSS_SELECTOR, div0)
            div1progress_bar = div0progress_bar.find_element(By.CSS_SELECTOR, div1)

            with suppress(NoSuchElementException):
                progress_bar = div1progress_bar.find_element(By.CSS_SELECTOR, div2)

            if progress_bar is None:
                break

    def scroll_to(self, element: WebElement) -> None:
        """Scroll to a specific web element.

        Args:
            element (WebElement): The web element to scroll to.

        """
        action = ActionChains(self.driver)
        action.scroll_to_element(element)
        sleep(0.5)

    def Select2_ELAW(self, elementSelect: str, to_Search: str) -> None:  # noqa: N802, N803
        """Select an option from a Select2 dropdown based on the search text.

        Args:
            elementSelect (str): The CSS selector of the Select2 element.
            to_Search (str): The text to search and select.

        """
        selector: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, elementSelect)))

        items = selector.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        elementsSelecting = elementSelect.replace("'", "'")  # noqa: N806
        if '"' in elementsSelecting:
            elementsSelecting = elementSelect.replace('"', "'")  # noqa: N806

        for item in items:
            value_item = item.get_attribute("value")
            cms = f"{elementsSelecting} > option[value='{value_item}']"
            text_item = self.driver.execute_script(f'return $("{cms}").text();')

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_Search.upper())

        if value_opt:
            command = f"$('{elementSelect}').val(['{value_opt}']);"
            command2 = f"$('{elementSelect}').trigger('change');"

            if "'" in elementSelect:
                command = f"$(\"{elementSelect}\").val(['{value_opt}']);"
                command2 = f"$(\"{elementSelect}\").trigger('change');"

            self.driver.execute_script(command)
            self.driver.execute_script(command2)
