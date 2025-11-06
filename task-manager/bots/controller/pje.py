"""Módulo para a classe de controle dos robôs PJe."""

import json.decoder
from contextlib import suppress
from threading import Lock
from typing import TYPE_CHECKING, ClassVar

from dotenv import load_dotenv

from app.interfaces._pje import DictResults, DictSeparaRegiao
from app.types._custom import StrProcessoCNJ
from bots.head import CrawJUD
from bots.resources import RegioesIterator
from bots.resources.elements import pje as el
from common.exceptions.validacao import ValidacaoStringError
from constants import HTTP_OK_STATUS

load_dotenv()

if TYPE_CHECKING:
    from httpx import Client

    from app.interfaces import BotData
    from app.types import AnyType, Dict


class PjeBot(CrawJUD):
    """Classe de controle para robôs do PJe."""

    posicoes_processos: ClassVar[Dict] = {}

    def get_headers_cookies(
        self,
    ) -> tuple[dict[str, str], dict[str, str]]:
        cookies_driver = self.driver.get_cookies()
        har_data_ = self.driver.requests

        entry_proxy = list(
            filter(
                lambda item: f"https://pje.trt{self.regiao}.jus.br/pje-comum-api/"
                in item.url,
                har_data_,
            ),
        )[-1]

        return (
            {
                str(header): str(value)
                for header, value in entry_proxy.headers.items()
            },
            {
                str(cookie["name"]): str(cookie["value"])
                for cookie in cookies_driver
            },
        )

    def search(
        self,
        data: dict,
        row: int,
        client: Client,
    ) -> DictResults | None:
        """Realize a busca de um processo no sistema PJe.

        Args:
            data (BotData): Dados do processo a serem consultados.
            row (int): Índice da linha do processo na planilha de entrada.
            client (Client): Instância do cliente HTTP para requisições ao sistema PJe.
            regiao (str):regiao

        Returns:
            DictResults | Literal["Nenhum processo encontrado"]: Resultado da busca do
            processo ou mensagem indicando que nenhum processo foi encontrado.

        """
        # Envia mensagem de log para task assíncrona
        id_processo: str
        numero_processo = data["NUMERO_PROCESSO"]
        message = f"Buscando processo {numero_processo}"
        self.print_message(
            message=message,
            row=row,
            message_type="log",
        )

        link = el.LINK_DADOS_BASICOS.format(
            trt_id=self.regiao,
            numero_processo=numero_processo,
        )

        response = client.get(url=link)

        if response.status_code != HTTP_OK_STATUS:
            self.print_message(
                message="Nenhum processo encontrado",
                message_type="error",
                row=row,
            )
            return None

        with suppress(json.decoder.JSONDecodeError, KeyError):
            data_request = response.json()
            if isinstance(data_request, list):
                data_request: dict[str, AnyType] = data_request[0]
            id_processo = data_request.get("id", "")

        if not id_processo:
            self.print_message(
                message="Nenhum processo encontrado",
                message_type="error",
                row=row,
            )
            return None

        url_ = el.LINK_CONSULTA_PROCESSO.format(
            trt_id=self.regiao,
            id_processo=id_processo,
        )
        result = client.get(url=url_)

        if not result:
            self.print_message(
                message="Nenhum processo encontrado",
                message_type="error",
                row=row,
            )
            return None

        return DictResults(
            id_processo=id_processo,
            data_request=result.json(),
        )

    pje_classes: ClassVar[dict[str, type[PjeBot]]] = {}
    subclasses_search: ClassVar[dict[str, type[PjeBot]]] = {}
    lock = Lock()

    @property
    def list_posicao_processo(self) -> dict[str, int]:
        return self.posicoes_processos

    @property
    def data_regiao(self) -> list[BotData]:
        return self._data_regiao

    @data_regiao.setter
    def data_regiao(self, _data_regiao: str) -> None:
        self._data_regiao = _data_regiao

    @property
    def regiao(self) -> str:
        return self._regiao

    @property
    def cookies(self) -> dict[str, str]:
        """Dicionário de Cookies."""
        return self._cookies

    @property
    def headers(self) -> dict[str, str]:
        """Dicionário de Headers."""
        return self._headers

    @property
    def base_url(self) -> str:
        """Dicionário de Cookies."""
        return self._base_url

    @regiao.setter
    def regiao(self, _regiao: str) -> None:
        self._regiao = _regiao

    def regioes(self) -> RegioesIterator:
        """Listagem das regiões do PJe.

        Returns:
            RegioesIterator:
                Iterator das Regiões do PJe.

        """
        return RegioesIterator(self)

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
                numero_processo = StrProcessoCNJ(
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
