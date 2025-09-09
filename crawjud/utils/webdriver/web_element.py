"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import platform
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Self

from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement

if TYPE_CHECKING:
    from crawjud.utils.webdriver import DriverBot as WebDriver


class WebElementBot[T](WebElement):
    """Gerencie e estenda funcionalidades de elementos WebDriver para automação web.

    Esta classe fornece métodos utilitários para interação avançada com elementos
    web, como cliques, preenchimento de campos, seleção em listas e manipulação
    de carregamentos dinâmicos, facilitando a automação de testes e rotinas web.

    """

    _cuurent_driver: WebDriver = None
    _action: ActionChains = None

    @classmethod
    def set_driver(cls, _driver: WebDriver) -> type[Self]:
        cls._cuurent_driver = _driver
        cls._action = ActionChains(_driver)

        return cls

    def click(self) -> None:
        """Perform a click action on a web element with brief pauses.

        Args:
            element (WebElement): The target web element.

        Implements a click with pre- and post-click delays.

        """
        sleep(0.05)
        super().click()
        sleep(0.05)

    def send_keys(self, word: T) -> None:
        send = None
        for key in dir(Keys):
            if getattr(Keys, key) == word:
                send = ""
                super().send_keys(word)
                break

        if send is None:
            for c in str(word):
                sleep(0.005)
                super().send_keys(c)

    def send_file(self, file: str | Path) -> None:
        file_ = file
        if isinstance(file, Path):
            if platform.system() == "Linux":
                file_ = file.as_posix()
            else:
                file_ = str(file)
        self._execute(
            Command.SEND_KEYS_TO_ELEMENT,
            {
                "text": "".join(keys_to_typing(file_)),
                "value": keys_to_typing(file_),
            },
        )

    def double_click(self) -> None:
        """Double-click on the given WebElement."""
        self._action.double_click(self).perform()

    def clear(self) -> None:
        self.click()
        sleep(0.5)
        super().clear()
        sleep(1)

    def display_none(self) -> None:
        """Wait for an element's display style to change to 'none'.

        Args:
            elemento (WebElement): The element to monitor.

        """
        while True:
            style = self.get_attribute("style")
            if "display: none;" not in style:
                sleep(0.01)
                break

    def scroll_to(self) -> None:
        """Scroll the view to the specified web element."""
        self._action.scroll_to_element(self)
        sleep(0.5)

    def find_element(
        self,
        by: str = By.ID,
        value: T | None = None,
    ) -> WebElementBot:
        return super().find_element(by=by, value=value)

    def find_elements(
        self,
        by: str = By.ID,
        value: T | None = None,
    ) -> list[WebElementBot]:
        return super().find_elements(by=by, value=value)

    def select2(self, to_search: str) -> None:
        r"""Select an option from a Select2 dropdown based on a search text.

        Args:
            to_search (str): The option text to search and select.

        """
        items = self.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        id_select = self.get_attribute("id")

        for item in items:
            value_item = item.get_attribute("value")

            cms = f"select#{id_select} > option[value='{value_item}']"
            text_item = self.driver.execute_script(
                f'return $("{cms}").text();',
            )

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_search.upper())

        if value_opt:
            command = f"$('select#{id_select}').val(['{value_opt}']);"
            command2 = f"$('select#{id_select}').trigger('change');"

            self._cuurent_driver.execute_script(command)
            self._cuurent_driver.execute_script(command2)
