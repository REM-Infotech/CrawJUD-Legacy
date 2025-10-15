"""Module for managing WebDriver instances and related utilities."""

import platform
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Self, TypedDict

from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select


class RectWebElement(TypedDict):
    """Dict Rect Webelement."""

    height: float
    width: float
    x: float
    y: float


class WebElementBot[T](WebElement):
    """Gerencie e estenda funcionalidades de elementos WebDriver para automação web.

    Esta classe fornece métodos utilitários para interação avançada com elementos
    web, como cliques, preenchimento de campos, seleção em listas e manipulação
    de carregamentos dinâmicos, facilitando a automação de testes e rotinas web.

    """

    _current_driver: WebDriver = None
    _action: ActionChains = None

    def __call__(self, *args, **kwds) -> None:
        return super().click()

    @classmethod
    def set_driver(cls, _driver: WebDriver) -> type[Self]:
        cls._current_driver = _driver
        cls._action = ActionChains(_driver)

        return cls

    @property
    def rect(self) -> RectWebElement:
        return super().rect

    @property
    def location(self) -> RectWebElement:
        return super().location

    def double_click(self) -> None:
        self._action.double_click(self).perform()

    def select_item(self, item: str) -> None:
        Select(self).select_by_value(item)

    def click(self) -> None:
        """Perform a click action on a web element with brief pauses.

        Args:
            element (WebElement): The target web element.

        Implements a click with pre- and post-click delays.

        """
        sleep(0.05)
        super().click()
        sleep(0.05)

    def clear(self) -> None:
        self.click()
        sleep(0.5)
        super().clear()
        sleep(1)

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

    def send_keys(self, word: T) -> None:
        send = False
        for key in dir(Keys):
            if getattr(Keys, key) == word:
                send = True
                super().send_keys(word)
                break

        if not send:
            for c in str(word):
                sleep(0.009)
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

            cms = f"select[id='{id_select}'] > option[value='{value_item}']"
            text_item = self._current_driver.execute_script(
                f'return $("{cms}").text();',
            )

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_search.upper())

        if value_opt:
            command = f"$('select#{id_select}').val(['{value_opt}']);"
            command2 = f"$('select#{id_select}').trigger('change');"

            self._current_driver.execute_script(command)
            self._current_driver.execute_script(command2)

    def scroll_from_origin(
        self,
        delta_x: int,
        delta_y: int,
        origin: Self | None = None,
    ) -> None:
        """Scrolls by provided amount based on a provided origin.

        The scroll origin is either the center of an element or the upper left of the
        viewport plus any offsets. If the origin is an element, and the element
        is not in the viewport, the bottom of the element will first be
        scrolled to the bottom of the viewport.

        Args:
            origin: Where scroll originates (viewport or element center) plus provided offsets.
            delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
            delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.

        """
        if not origin:
            origin = self

        location = origin.location
        scroll_origin = ScrollOrigin.from_element(
            origin,
            x_offset=location["x"],
            y_offset=location["y"],
        )

        self._action.scroll_to_element()

        with suppress(Exception):
            return self._action.scroll_from_origin(
                scroll_origin=scroll_origin,
                delta_x=0,
                delta_y=delta_y,
            ).perform()

    def scroll_to_element(self) -> None:
        """Scroll to element.

        If the element is outside the viewport, scrolls the bottom of the
        element to the bottom of the viewport.

        Args:
            element: Which element to scroll into the viewport.

        """
        self._action.scroll_to_element(self).perform()
