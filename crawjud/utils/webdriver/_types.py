from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Literal,
    ParamSpec,
    TypedDict,
    TypeVar,
)

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as GeckoOptions

if TYPE_CHECKING:
    from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.remote_connection import FirefoxRemoteConnection
    from selenium.webdriver.firefox.service import Service as GeckoService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager

P = ParamSpec("optionsConstructor")
BrowserOptions = Literal["chrome", "gecko", "firefox"]
TExtensionsPath = TypeVar("ExtensionsPath", bound=str | Path)

driver_options = TypeVar(
    "DriverOptions",
    bound=Callable[..., GeckoOptions] | Callable[..., ChromeOptions],
)

ChromePreferences = TypedDict(
    "ChromePreferences",
    {
        "download.prompt_for_download": bool,
        "plugins.always_open_pdf_externally": bool,
        "profile.default_content_settings.popups": int,
        "printing.print_preview_sticky_settings.appState": str,
        "download.default_directory": str,
        "credentials_enable_service": bool,
        "profile.password_manager_enabled": bool,
    },
)

FirefoxPreferences = TypedDict(
    "FirefoxPreferences",
    {
        "browser.download.folderList": int,
        "browser.download.manager.showWhenStarting": bool,
        "browser.download.dir": str,
        "browser.helperApps.neverAsk.saveToDisk": str,
        "pdfjs.disabled": bool,
    },
)


class ChromeConfig(TypedDict):
    name: str
    service: type[ChromeService]
    executor: type[ChromeRemoteConnection]
    options: driver_options
    manager: type[ChromeDriverManager]


class FirefoxConfig(TypedDict):
    name: str
    service: type[GeckoService]
    executor: type[FirefoxRemoteConnection]
    options: driver_options
    manager: type[GeckoDriverManager]
    args_executor: dict[str, str]


class OptionsConfig(TypedDict):
    chrome: ChromeConfig
    firefox: FirefoxConfig
    gecko: FirefoxConfig
