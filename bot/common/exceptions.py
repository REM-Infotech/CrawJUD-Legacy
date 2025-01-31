"""Module defining custom exceptions for CrawJUD bot."""

from bot.common.selenium_excepts import exceptionsBot, webdriver_exepts


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""


class CrawJUDExceptions(Exception):
    """Base exception class for CrawJUD-specific errors."""

    message_: str = None

    @property
    def message(self):
        """Get the error message."""
        return self.message_

    @message.setter
    def message(self, message: str):
        """Set the error message."""
        self.message_ = message

    def __init__(self, message: str = None, e: Exception = None, *args, **kwargs):
        """Initialize CrawJUDExceptions with an optional message and exception.

        Args:
            message (str, optional): Error message. Defaults to None.
            e (Exception, optional): Original exception. Defaults to None.
        """
        self.message = message

        if isinstance(e, ErroDeExecucao):
            self.message = e.message

        elif message is None:
            self.message = exceptionsBot().get(
                e.__class__.__name__, "".join(getattr(e, "args", ["Erro Interno"]))
            )

        super().__init__(self.message)

    def __str__(self):
        """Return the string representation of the exception."""
        return self.message

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized exception."""
        check_except = instance in webdriver_exepts()
        return check_except


class ItemNaoEcontrado(CrawJUDExceptions):
    """Exception raised when a required item is not found."""

    def __init__(self, message="Item não encontrado"):
        """Initialize ItemNaoEcontrado with a default message."""
        super().__init__(message)

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized exception."""
        return super().__instancecheck__(instance)

    def __str__(self):
        """Return the string representation of the exception."""
        return super().__str__()


class ErroDeExecucao(CrawJUDExceptions):
    """Exception raised for errors during CrawJUD execution.

    This exception is a subclass of CrawJUDExceptions and is used to indicate
    that an error occurred during the execution of a CrawJUD process.

    Methods:
        __instancecheck__(instance: Exception) -> bool:
            Check if the instance is an exception.
        __str__() -> str:
            Return the string representation of the exception.
    """

    def __init__(self, *args, **kwargs):
        """Initialize ErroDeExecucao with optional arguments."""
        super().__init__(*args, **kwargs)

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized exception."""
        return super().__instancecheck__(instance)

    def __str__(self):
        """Return the string representation of the exception."""
        return super().__str__()
