from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
)
from urllib3.exceptions import MaxRetryError


def webdriver_exepts() -> list[Exception]:

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
    ]


def exeptionsBot() -> dict[Exception, str]:

    return {
        TimeoutException: "Falha ao encontrar elemento",
        StaleElementReferenceException: "Erro ao encontrar referencia do elemento",
        NoSuchElementException: "Elemento não encontrado",
        ElementNotInteractableException: "Não foi possível interagir com o elemento",
        ElementClickInterceptedException: "Click interceptado",
        ValueError: "Erro de informação",
        Exception: "Erros diversos",
    }
