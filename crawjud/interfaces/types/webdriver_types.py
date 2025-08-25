"""Tipos e configurações para opções e preferências de WebDriver Selenium.

Este módulo fornece definições de tipos, TypedDicts e aliases para configuração
de navegadores Chrome e Firefox, facilitando a tipagem e reutilização de opções
e preferências em automações Selenium.
"""

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
    from selenium.webdriver.chrome.remote_connection import (
        ChromeRemoteConnection,
    )
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.remote_connection import (
        FirefoxRemoteConnection,
    )
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
    """Defina configurações específicas para o WebDriver Chrome Selenium.

    Args:
        name (str): Nome identificador da configuração do navegador.
        service (type[ChromeService]): Classe de serviço do ChromeDriver.
        executor (type[ChromeRemoteConnection]): Executor de conexão remota.
        options (driver_options): Função construtora das opções do Chrome.
        manager (type[ChromeDriverManager]): Gerenciador do ChromeDriver.

    Returns:
        dict: Dicionário tipado com as configurações do Chrome.

    """

    name: str
    service: type[ChromeService]
    executor: type[ChromeRemoteConnection]
    options: driver_options
    manager: type[ChromeDriverManager]


class FirefoxConfig(TypedDict):
    """Defina configurações específicas para o WebDriver Firefox Selenium.

    Args:
        name (str): Nome identificador da configuração do navegador.
        service (type[GeckoService]): Classe de serviço do GeckoDriver.
        executor (type[FirefoxRemoteConnection]): Executor de conexão remota.
        options (driver_options): Função construtora das opções do Firefox.
        manager (type[GeckoDriverManager]): Gerenciador do GeckoDriver.
        args_executor (dict[str, str]): Argumentos adicionais para o executor.

    Returns:
        dict: Dicionário tipado com as configurações do Firefox.

    """

    name: str
    service: type[GeckoService]
    executor: type[FirefoxRemoteConnection]
    options: driver_options
    manager: type[GeckoDriverManager]
    args_executor: dict[str, str]


class OptionsConfig(TypedDict):
    """Defina configurações agrupadas para múltiplos navegadores Selenium.

    Args:
        chrome (ChromeConfig): Configuração específica para o Chrome.
        firefox (FirefoxConfig): Configuração específica para o Firefox.
        gecko (FirefoxConfig): Configuração específica para o GeckoDriver.

    Returns:
        dict: Dicionário tipado com as configurações de todos os navegadores.

    """

    chrome: ChromeConfig
    firefox: FirefoxConfig
    gecko: FirefoxConfig
