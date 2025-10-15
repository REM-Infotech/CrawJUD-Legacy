"""Módulo para a classe de controle dos robôs PJe."""

from __future__ import annotations

import json.decoder
import platform
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Lock
from time import perf_counter, sleep
from typing import TYPE_CHECKING, ClassVar, Literal

from dotenv import dotenv_values
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app.common.exceptions.bot import (
    raise_start_error,
)
from app.common.exceptions.validacao import ValidacaoStringError
from app.controllers.main import CrawJUD
from app.interfaces.types import BotData
from app.interfaces.types.bots.pje import (
    DictResults,
    DictSeparaRegiao,
    Processo,
)
from app.interfaces.types.custom import StrProcessoCNJ
from app.resources.elements import pje as el
from app.utils.iterators import RegioesIterator
from app.utils.models.logs import CachedExecution

if TYPE_CHECKING:
    from httpx import Client

    from app.interfaces.dict.bot import BotData


DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()
environ = dotenv_values()
HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class PjeBot(CrawJUD):
    """Classe de controle para robôs do PJe."""

    def __init__(
        self,
        current_task: ContextTask = None,
        storage_folder_name: str | None = None,
        name: str | None = None,
        system: str | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        """Instancia a classe."""
        self.botname = name
        self.botsystem = system

        self.folder_storage = storage_folder_name
        self.current_task = current_task
        self.start_time = perf_counter()
        self.pid = str(current_task.request.id)

        selected_browser = "chrome"
        if platform.system() == "Linux":
            selected_browser = "firefox"

        super().__init__(
            selected_browser=selected_browser,
            with_proxy=True,
            *args,
            **kwargs,
        )

        for k, v in kwargs.copy().items():
            setattr(self, k, v)

        self.download_files()

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

            raise_start_error("Falha na autenticação.")

        self.print_msg(
            message="Sucesso na autenticação!",
            type_log="info",
        )
        self._frame = self.load_data()

        sleep(0.5)
        self.print_msg(
            message="Execução inicializada!",
            type_log="info",
        )

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
        data: BotData,
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
                data_request: dict[str, T] = data_request[0]
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

    def save_success_cache(
        self,
        data: Processo,
        processo: StrProcessoCNJ | None = None,
    ) -> None:
        """Salva os resultados em cache Redis.

        Arguments:
            data (Processo): Mapping com as informações extraídas do processo
            processo (StrProcessoCNJ): Número do Processo


        """
        with suppress(Exception):
            cache = CachedExecution(
                processo=processo.data,
                data=data,
                pid=self.pid,
            )
            cache.save()

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
