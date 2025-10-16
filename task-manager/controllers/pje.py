"""Módulo para a classe de controle dos robôs PJe."""

import json.decoder
from _types import AnyType
from _types._custom import StrProcessoCNJ
from contextlib import suppress
from threading import Lock
from time import sleep
from typing import TYPE_CHECKING, ClassVar, Literal

from _interfaces import BotData
from _interfaces.pje import DictResults, DictSeparaRegiao
from common.exceptions.validacao import ValidacaoStringError
from resources import RegioesIterator
from resources.elements import pje as el
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from controllers._master import CrawJUD

if TYPE_CHECKING:
    from httpx import Client


class PjeBot(CrawJUD):
    """Classe de controle para robôs do PJe."""

    def get_headers_cookies(
        self,
        regiao: str,
    ) -> tuple[dict[str, str], dict[str, str]]:
        cookies_driver = self.driver.get_cookies()
        har_data_ = self.driver.current_har
        entries = list(har_data_.entries)

        entry_proxy = [
            item
            for item in entries
            if f"https://pje.trt{regiao}.jus.br/pje-comum-api/"
            in item.request.url
        ][-1]

        return (
            {
                str(header["name"]): str(header["value"])
                for header in entry_proxy.request.headers
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
        regiao: str,
    ) -> DictResults | Literal["Nenhum processo encontrado"]:
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
        trt_id = regiao
        numero_processo = data["NUMERO_PROCESSO"]
        message = f"Buscando processo {numero_processo}"
        self.print_msg(
            message=message,
            row=row,
            type_log="log",
        )

        link = el.LINK_DADOS_BASICOS.format(
            trt_id=trt_id,
            numero_processo=numero_processo,
        )

        response = client.get(url=link)

        if response.status_code != 200:
            return "Nenhum processo encontrado"

        with suppress(json.decoder.JSONDecodeError, KeyError):
            data_request = response.json()
            if isinstance(data_request, list):
                data_request: dict[str, AnyType] = data_request[0]
            id_processo = data_request.get("id", "")

        if not id_processo:
            return "Nenhum processo encontrado"

        url_ = el.LINK_CONSULTA_PROCESSO.format(
            trt_id=trt_id,
            id_processo=id_processo,
        )
        result = client.get(url=url_)

        if not result:
            return "Nenhum processo encontrado"

        return DictResults(
            id_processo=id_processo,
            data_request=result.json(),
        )

    def auth(
        self,
    ) -> bool:
        try:
            driver = self.driver
            wait = self.wait
            driver.get("https://www.jus.br")

            sleep(5)

            btn_certificado = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ('div[class="certificado"] > a'),
                )),
            )
            event_cert = btn_certificado.get_attribute("onclick")
            driver.execute_script(event_cert)
            try:
                WebDriverWait(
                    driver=driver,
                    timeout=60,
                    poll_frequency=0.3,
                    ignored_exceptions=(UnexpectedAlertPresentException),
                ).until(ec.url_to_be("https://www.jus.br/"))
            except TimeoutException:
                if "pjekz" not in driver.current_url:
                    return False

            if (
                "pjekz/painel/usuario-externo" in driver.current_url
                or "pjekz" in driver.current_url
            ):
                driver.refresh()

        except Exception:
            self.print_msg(
                "Erro ao realizar autenticação",
                type_log="error",
            )
            return False

        return True

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

        for item in self._frame:
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

    def formata_url_pje(
        self,
        regiao: str,
        _format: str = "login",
    ) -> str:
        """Formata a URL no padrão esperado pelo PJe.

        Returns:
            str: URL formatada.

        """
        formats = {
            "login": f"https://pje.trt{regiao}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{regiao}.jus.br/pjekz/",
            "search": f"https://pje.trt{regiao}.jus.br/consultaprocessual/",
        }

        return formats[_format]
