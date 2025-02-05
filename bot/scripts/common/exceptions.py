"""Module: exceptions.

This module defines custom exception classes for the CrawJUD-Bots application, facilitating error handling and reporting.
"""  # noqa: E501

from bot.common.selenium_excepts import exceptionsBot, webdriver_exepts


class StartError(Exception):
    """StartError Exception.

    Raised for errors that occur during the initialization or start of the bot.
    """

    pass


class CrawJUDExceptions(Exception):  # noqa: N818
    """CrawJUDExceptions Class.

    Base class for all CrawJUD-related exceptions, providing a standardized way to handle errors.
    """

    message_: str = None

    @property
    def message(self):
        """str: The error message associated with the exception."""
        return self.message_

    @message.setter
    def message(self, message: str):
        """Set the error message for the exception.

        Args:
            message (str): The error message to associate with the exception.

        """
        self.message_ = message

    def __init__(self, message: str = None, e: Exception = None, *args, **kwargs):
        """Initialize a new CrawJUDExceptions instance.

        Args:
            message (str, optional): The error message.
            e (Exception, optional): The original exception that caused this exception.
            *args: Variable length argument list.
            **kwargs: Variable keyword arguments.

        Raises:
            CrawJUDExceptions: Raises itself with the appropriate message.

        """
        self.message = message

        if isinstance(e, ErroDeExecucao):
            self.message = e.message

        elif message is None:
            self.message = exceptionsBot().get(e.__class__.__name__, "".join(getattr(e, "args", ["Erro Interno"])))

        super().__init__(self.message)

    def __str__(self):
        """str: The string representation of the exception."""
        return self.message

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is a recognized CrawJUD exception.

        Args:
            instance (Exception): The exception instance to check.

        Returns:
            bool: True if the instance is a recognized CrawJUD exception, False otherwise.

        """
        check_except = instance in webdriver_exepts()
        return check_except


class ItemNaoEcontrado(CrawJUDExceptions):
    """ItemNaoEcontrado Exception.

    Raised when a required item or resource is not found.
    """

    def __init__(self, message="Item não encontrado"):
        """Initialize a new ItemNaoEcontrado instance.

        Args:
            message (str, optional): The error message. Defaults to "Item não encontrado".

        """
        super().__init__(message)

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is an ItemNaoEcontrado exception.

        Args:
            instance (Exception): The exception instance to check.

        Returns:
            bool: True if the instance is an ItemNaoEcontrado exception, False otherwise.

        """
        return super().__instancecheck__(instance)

    def __str__(self):
        """str: The string representation of the exception."""
        return super().__str__()


class ErroDeExecucao(CrawJUDExceptions):
    """ErroDeExecucao Exception.

    Raised for errors that occur during the execution of CrawJUD processes.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new ErroDeExecucao instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Variable keyword arguments.

        """
        super().__init__(*args, **kwargs)

    def __instancecheck__(self, instance: Exception) -> bool:
        """Check if the instance is an ErroDeExecucao exception.

        Args:
            instance (Exception): The exception instance to check.

        Returns:
            bool: True if the instance is an ErroDeExecucao exception, False otherwise.

        """
        return super().__instancecheck__(instance)

    def __str__(self):
        """str: The string representation of the exception."""
        return super().__str__()
