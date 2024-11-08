from ...CrawJUD import CrawJUD


class BaseElementsBot(CrawJUD):

    from .properties import Configuracao
    from .esaj import ESAJ_AM
    from .projudi import PROJUDI_AM
    from .elaw import AME
    from .pje import PJE_AM

    funcs = {
        "esaj": {"AM": ESAJ_AM},
        "projudi": {"AM": PROJUDI_AM},
        "elaw": {"AME": AME},
    }

    def __init__(self, *args, **kwrgs):
        """### ElementsBot"""

    @property
    def Elements(self):
        """Retorna a configuração de acordo com o estado ou cliente."""
        dados = self.funcs.get(self.system).get(self.state_or_client)

        if not dados:
            raise AttributeError("Estado ou cliente não encontrado.")

        return self.Configuracao(dados.__dict__)


class ElementsBot(BaseElementsBot):

    def __init__(self, *args, **kwrgs):
        BaseElementsBot.__init__(self, *args, **kwrgs)
