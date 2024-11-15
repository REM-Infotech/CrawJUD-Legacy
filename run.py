import os
import json
import argparse


class WorkerThread:

    @property
    def BotStarter(self):  # -> Hints:

        from bot.scripts.pje import pje
        from bot.scripts.esaj import esaj
        from bot.scripts.elaw import elaw
        from bot.scripts.caixa import caixa
        from bot.scripts.projudi import projudi
        from bot.scripts.calculadoras import calculadoras

        systems = {
            "pje": pje,
            "esaj": esaj,
            "elaw": elaw,
            "caixa": caixa,
            "projudi": projudi,
            "calculadoras": calculadoras,
        }

        return systems.get(self.system)

    # argv: str = None, botname: str = None
    def __init__(self, **kwrgs: dict[str, str]):
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)

    def start(self) -> int:

        try:

            self.BotStarter(**self.kwrgs)

        except Exception:
            return 500


# Cria o parser
parser = argparse.ArgumentParser(
    description="Exemplo de argumentos não mapeados com zero ou mais valores"
)

# Captura os argumentos conhecidos e desconhecidos
args, unknown_args = parser.parse_known_args()

# Para os argumentos desconhecidos, você pode armazená-los em um dicionário ou outra estrutura
kwargs = {}
for i in range(0, len(unknown_args), 2):
    key = unknown_args[i].lstrip("-")
    value = unknown_args[i + 1] if i + 1 < len(unknown_args) else None
    kwargs.update({key: value})

with open(
    os.path.join(kwargs.get("path_args"), f"OS_PID {kwargs.get("pid")}.txt"), "w"
) as f:
    f.write(os.getpid())

WorkerThread(**kwargs).start()
