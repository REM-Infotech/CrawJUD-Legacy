from ...CrawJUD import CrawJUD


class BaseElementsBot(CrawJUD):

    from .elaw import AME
    from .esaj import ESAJ_AM
    from .pje import PJE_AM
    from .projudi import PROJUDI_AM
    from .properties import Configuracao

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
        state_or_client = self.state_or_client
        if " " in state_or_client:
            state_or_client = state_or_client.split(" ")[0]
        dados = self.funcs.get(self.system).get(state_or_client)

        if not dados:
            raise AttributeError("Estado ou cliente não encontrado.")

        return self.Configuracao(dados.__dict__)


class ElementsBot(BaseElementsBot):

    def __init__(self, *args, **kwrgs):
        BaseElementsBot.__init__(self, *args, **kwrgs)
