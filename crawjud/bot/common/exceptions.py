"""Module defining custom exceptions for CrawJUD bot."""

from crawjud.bot.common.selenium_excepts import exceptionsBot, webdriver_exepts


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""


class BaseCrawJUDError(Exception):
    """Base exception class for CrawJUD-specific errors."""

    message_: str = None

    @property
    def message(self) -> str:
        """Get the error message."""
        return self.message_

    @message.setter
    def message(self, message: str) -> None:
        """Set the error message."""
        self.message_ = message

    def __init__(
        self,
        message: str = None,
        e: Exception = None,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize BaseCrawJUDError with an optional message and exception.

        Args:
            message (str, optional): Error message. Defaults to None.
            e (Exception, optional): Original exception. Defaults to None.
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        self.message = message

        if isinstance(e, ExecutionError):
            self.message = e.message

        elif message is None:
            self.message = exceptionsBot().get(e.__class__.__name__, "".join(getattr(e, "args", ["Erro Interno"])))

        super().__init__(self.message)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        Returns:
            str: The error message.

        """
        return self.message

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized exception.

        Returns:
            bool: True if the instance is a recognized exception, False otherwise.

        """
        check_except = instance in webdriver_exepts()
        return check_except


class NotFoundError(BaseCrawJUDError):
    """Exception raised when a required item is not found."""

    def __init__(
        self,
        message: str = "Item não encontrado",
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize NotFoundError with a default message.

        Args:
            message (str, optional): Error message. Defaults to "Item não encontrado".
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        super().__init__(message)

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized exception.

        Returns:
            bool: True if the instance is a recognized exception, False otherwise.

        """
        return super().__instancecheck__(instance)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        Returns:
            str: The error message.

        """
        return super().__str__()


class ExecutionError(BaseCrawJUDError):
    """Exception raised for errors during CrawJUD execution.

    This exception is a subclass of BaseCrawJUDError and is used to indicate
    that an error occurred during the execution of a CrawJUD process.

    Methods:
        __instancecheck__(instance: Exception) -> bool:
            Check if the instance is an exception.
        __str__() -> str:
            Return the string representation of the exception.

    """

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize ExecutionError with optional arguments.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        super().__init__(*args, **kwargs)

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized exception.

        Returns:
            bool: True if the instance is a recognized exception, False otherwise.

        """
        return super().__instancecheck__(instance)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        Returns:
            str: The error message.

        """
        return super().__str__()
