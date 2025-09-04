"""Handler de erros do selenium."""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)


class SeleniumError(
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    UnexpectedAlertPresentException,
    StaleElementReferenceException,
):
    """Handler de erros do selenium."""
