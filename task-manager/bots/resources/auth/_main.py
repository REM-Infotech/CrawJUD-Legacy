from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait
    from seleniumwire.webdriver import Chrome

    from bots.head import CrawJUD
    from bots.resources.queues.print_message import PrintMessage


class AutenticadorBot:
    def __init__(self, bot: CrawJUD) -> None:
        self.bot = bot

    @property
    def driver(self) -> WebDriver | Chrome:
        return self.bot.driver

    @property
    def wait(self) -> WebDriverWait[WebDriver | Chrome]:
        return self.bot.wait

    @property
    def print_message(self) -> PrintMessage:
        return self.bot.print_message

    @property
    def bot_data[T](self) -> T:
        return self.bot.bot_data
