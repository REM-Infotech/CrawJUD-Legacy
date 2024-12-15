from bot.common.selenium_excepts import exceptionsBot, webdriver_exepts


class CrawJUDExceptions(Exception):
    """Exceção base personalizada."""

    _errmsg: str = ""
    _except_captured = Exception

    @property
    def message_err(self):
        return self._errmsg

    @message_err.setter
    def message_err(self, new_msg: str):
        self._errmsg = new_msg

    @property
    def except_captured(self):
        return self._except_captured

    @except_captured.setter
    def except_captured(self, excep_capt: Exception):
        self._except_captured = excep_capt

    def __init__(self, message: str, e: Exception = None):

        message_error = None
        if e:

            name_Except = e.__class__.__name__
            message_error = str(exceptionsBot().get(name_Except))

        if message_error:
            message = message_error

        self.message_err = message
        self.except_captured = e

        if isinstance(message, Exception):
            self.except_captured = message

            name_Except = message.__class__.__name__
            message_error = exceptionsBot().get(name_Except)

            if message_error is None:
                message = "Erro interno, contactar suporte"

            self.message_err = str(message)

        super().__init__(message)

    def __str__(self):
        return self.message_err

    def __instancecheck__(self, instance: Exception) -> bool:

        check_except = instance in webdriver_exepts() or isinstance(
            instance, type(self.except_captured)
        )
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
    """Exceção para quando um recurso não é encontrado."""

    def __init__(self, message: str = "Erro ao executar operação", e: Exception = None):
        super().__init__(message, e)

    def __instancecheck__(self, instance: Exception) -> bool:
        return super().__instancecheck__(instance)

    def __str__(self):
        return super().__str__()
