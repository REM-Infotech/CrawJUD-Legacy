from contextlib import suppress
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING

from app.interfaces._pje import DictResults
from bots.resources.elements import pje as el
from bots.resources.search._main import SearchBot
from constants import HTTP_OK_STATUS

if TYPE_CHECKING:
    from httpx import Client

    from app.types import AnyType


class PjeSeach(SearchBot):
    def __call__(
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

        with suppress(JSONDecodeError, KeyError):
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
