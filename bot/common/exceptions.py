from bot.common.selenium_excepts import exeptionsBot


class CrawJUDExceptions(Exception):
    """Exceção base personalizada."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ItemNaoEcontrado(CrawJUDExceptions):
    """Exceção para quando um recurso não é encontrado."""

    def __init__(self, message="Item não encontrado"):
        super().__init__(message)


class ErroDeExecucao(CrawJUDExceptions):
    """Exceção para quando um recurso não é encontrado."""

    def __init__(self, message: str = "Erro ao executar operação", e: Exception = None):

        message_error = ""
        if e:
            exceptBots = exeptionsBot()
            message_error: str = getattr(e, "msg", getattr(e, "message", ""))

            if message_error == "":
                typeexept = type(e)
                message_error = str(exceptBots.get(typeexept, ""))

        if message_error:
            message = message_error

        super().__init__(message)
