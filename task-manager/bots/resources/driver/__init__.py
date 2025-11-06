"""Gerenciador do webdriver para a execução dos bots."""

from typing import TYPE_CHECKING

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome as ChromeWired
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from constants import WORKDIR
from constants.webdriver import ARGUMENTS, PREFERENCES, SETTINGS

from .web_element import WebElementBot

if TYPE_CHECKING:
    from bots.head import CrawJUD


class BotDriver:
    """Gerenciador do webdriver para a execução dos bots."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instanciamento do gerenciador do webdriver para a execução dos bots."""
        options = Options()
        user_data_dir = WORKDIR.joinpath("chrome-data", bot.pid)
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_data_dir.chmod(0o775)

        options.add_argument(f"--user-data-dir={user_data_dir!s}")

        for argument in ARGUMENTS:
            options.add_argument(argument)

        if "projudi" in bot.config.get("sistema"):
            options.add_argument("--incognito")

        download_dir = str(bot.output_dir_path)
        preferences = PREFERENCES
        preferences.update({
            "download.default_directory": download_dir,
            "printing.print_preview_sticky_settings.appState": SETTINGS,
        })

        options.add_experimental_option("prefs", preferences)

        for root, _, files in WORKDIR.joinpath(
            "chrome-extensions"
        ).walk():
            for file in filter(lambda x: x.endswith(".crx"), files):
                options.add_extension(str(root.joinpath(file)))

        if bot.config.get("sistema") != "pje":
            cache_manager = DriverCacheManager()
            driver_manager = ChromeDriverManager(
                cache_manager=cache_manager
            )
            service = Service(executable_path=driver_manager.install())
            self.driver = Chrome(options=options, service=service)

        else:
            self.driver = ChromeWired(options=options)

        self.driver._web_element_cls = WebElementBot
        self.wait = WebDriverWait(self.driver, 30)
