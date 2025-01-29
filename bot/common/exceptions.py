from bot.common.selenium_excepts import exceptionsBot, webdriver_exepts


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""


class CrawJUDExceptions(Exception):
    message_: str = None

    @property
    def message(self):
        return self.message_

    @message.setter
    def message(self, message: str):
        self.message_ = message

    def __init__(self, message: str = None, e: Exception = None, *args, **kwargs):
        self.message = message

        if isinstance(e, ErroDeExecucao):
            self.message = e.message

        elif message is None:
            self.message = exceptionsBot().get(
                e.__class__.__name__, "".join(getattr(e, "args", ["Erro Interno"]))
            )

        super().__init__(self.message)

    def __str__(self):
        return self.message

    def __instancecheck__(self, instance: Exception) -> bool:
        check_except = instance in webdriver_exepts()
        return check_except


class ItemNaoEcontrado(CrawJUDExceptions):
    """Exceção para quando um recurso não é encontrado."""

    def __init__(self, message="Item não encontrado"):
        super().__init__(message)

    def __instancecheck__(self, instance: Exception) -> bool:
        return super().__instancecheck__(instance)

    def __str__(self):
        return super().__str__()


class ErroDeExecucao(CrawJUDExceptions):
    """Exception raised for errors in the execution of CrawJUD.

    This exception is a subclass of CrawJUDExceptions and is used to indicate
    that an error occurred during the execution of a CrawJUD process.

    Methods:
        __instancecheck__(instance: Exception) -> bool:
            Check if the instance is an exception.
        __str__() -> str:
            Return the string representation of the exception.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __instancecheck__(self, instance: Exception) -> bool:
        return super().__instancecheck__(instance)

    def __str__(self):
        return super().__str__()
