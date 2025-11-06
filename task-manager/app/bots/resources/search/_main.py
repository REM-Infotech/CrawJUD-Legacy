from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait
    from seleniumwire.webdriver import Chrome

    from app.bots.head import CrawJUD
    from app.bots.resources.queues.print_message import PrintMessage
    from app.interfaces import BotData


class SearchBot:
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
    def bot_data(self) -> BotData:
        return self.bot.bot_data
