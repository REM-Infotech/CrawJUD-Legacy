"""Módulo de agrupamento de Iterators para o CrawJUD."""

from typing import TYPE_CHECKING

from common.exceptions.validacao import ValidacaoStringError

from app.types.bot import ProcessoCNJ

if TYPE_CHECKING:
    from app.controllers.pje import PjeBot
    from app.interfaces import BotData
    from app.interfaces._pje import DictSeparaRegiao


class RegioesIterator:
    """Retorne regiões e dados associados iterando sobre processos separados.

    Args:
        bot (PjeBot): Instância do bot para acessar métodos e dados.

    Returns:
        RegioesIterator: Iterador sobre tuplas (região, dados da região).

    Raises:
        StopIteration: Quando todas as regiões forem iteradas.

    """

    def __init__(self, bot: PjeBot) -> None:
        """Inicialize o iterador de regiões com dados do bot e processos separados.

        Args:
            bot (PjeBot): Instância do bot para acessar métodos e dados.


        """
        # Carrega arquivos e separa regiões
        dict_processo_separado: DictSeparaRegiao = self.separar_regiao()
        self._bot = bot
        self._regioes = list(dict_processo_separado["regioes"].items())
        self._posicoes_processos_planilha = dict_processo_separado[
            "position_process"
        ]
        self._index = 0

        # Atualiza atributos do bot
        bot.posicoes_processos = self._posicoes_processos_planilha
        bot.total_rows = len(self._posicoes_processos_planilha.values())

    def __iter__(self) -> RegioesIterator:
        """Retorne o próprio iterador para permitir iteração sobre regiões.

        Returns:
            RegioesIterator: O próprio iterador de regiões.

        """
        return self

    def __next__(self) -> tuple[str, list[BotData]]:
        """Implementa a iteração retornando próxima região e dados associados.

        Returns:
            tuple[str, str]: Tupla contendo a região e os dados da região.

        Raises:
            StopIteration: Quando todas as regiões forem iteradas.

        """
        if self._index >= len(self._regioes):
            raise StopIteration

        regiao, data_regiao = self._regioes[self._index]
        self._bot.regiao = regiao
        self._bot.data_regiao = data_regiao
        self._index += 1
        return regiao, data_regiao

    def separar_regiao(self) -> DictSeparaRegiao:
        """Separa os processos por região a partir do número do processo.

        Returns:
            dict[str, list[BotData] | dict[str, int]]: Dicionário com as regiões e a
            posição de cada processo.

        """
        regioes_dict: dict[str, list[BotData]] = {}
        position_process: dict[str, int] = {}

        for item in self.frame:
            try:
                numero_processo = ProcessoCNJ(
                    item["NUMERO_PROCESSO"],
                )

                regiao = numero_processo.tj
                # Atualiza o número do processo no item
                item["NUMERO_PROCESSO"] = str(numero_processo)
                # Adiciona a posição do processo na
                # lista original no dicionário de posições
                position_process[numero_processo] = len(
                    position_process,
                )

                # Caso a região não exista no dicionário, cria uma nova lista
                if not regioes_dict.get(regiao):
                    regioes_dict[regiao] = [item]
                    continue

                # Caso a região já exista, adiciona o item à lista correspondente
                regioes_dict[regiao].append(item)

            except ValidacaoStringError:
                continue

        return {
            "regioes": regioes_dict,
            "position_process": position_process,
        }
