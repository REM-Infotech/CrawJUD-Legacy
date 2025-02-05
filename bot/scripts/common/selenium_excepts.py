"""Module: selenium_excepts.

This module defines exceptions related to Selenium WebDriver interactions and provides utility functions for handling them.
"""  # noqa: E501

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
)
from urllib3.exceptions import MaxRetryError, ProtocolError


def webdriver_exepts() -> list[Exception]:
    """Retrieve a list of Selenium and related WebDriver exceptions.

    Returns:
        list[Exception]: A list containing various exception classes related to Selenium WebDriver.

    """
    return [
        TimeoutException,
        StaleElementReferenceException,
        NoSuchElementException,
        ElementNotInteractableException,
        ElementClickInterceptedException,
        ValueError,
        Exception,
        NoSuchWindowException,
        MaxRetryError,
        ProtocolError,
    ]


def exceptionsBot() -> dict[str, str]:  # noqa: N802
    """Provide a mapping of exception names to user-friendly error messages.

    Returns:
        dict[str, str]: A dictionary where keys are exception class names and values are descriptive error messages.

    """
    return {
        "TimeoutException": "Falha ao encontrar elemento",
        "StaleElementReferenceException": "Erro ao encontrar referencia do elemento",
        "NoSuchElementException": "Elemento não encontrado",
        "ElementNotInteractableException": "Não foi possível interagir com o elemento",
        "ElementClickInterceptedException": "Click interceptado",
        "ValueError": "Erro de informação",
        "Exception": "Erros diversos",
    }
