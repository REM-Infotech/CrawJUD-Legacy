"""Module for handling Selenium exceptions within the CrawJUD-Bots project."""

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
    """
    Return a list of Selenium and related exceptions.

    Returns:
        list[Exception]: A list containing various exception classes.
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


def exceptionsBot() -> dict[str, str]:
    """
    Provide a mapping of exception names to their corresponding messages.

    Returns:
        dict[str, str]: A dictionary mapping exception class names to error messages.
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
