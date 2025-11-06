"""Módulo para a classe de controle dos robôs PJe."""

import json.decoder
from contextlib import suppress
from os import environ
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, ClassVar

import pyotp
from dotenv import load_dotenv
from pykeepass import PyKeePass
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
)
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app.interfaces import BotData
from app.interfaces._pje import DictResults, DictSeparaRegiao
from app.types import AnyType, Dict
from app.types._custom import StrProcessoCNJ
from bots.head import CrawJUD
from bots.resources import AutenticadorPJe, RegioesIterator
from bots.resources.elements import pje as el
from common.exceptions.validacao import ValidacaoStringError

load_dotenv()

if TYPE_CHECKING:
    from httpx import Client


def _get_otp_uri() -> str:
    file_db = str(Path(environ.get("KBDX_PATH")))
    file_pw = environ.get("KBDX_PASSWORD")
    kp = PyKeePass(filename=file_db, password=file_pw)

    return kp.find_entries(
        otp=".*",
        url="https://sso.cloud.pje.jus.br/",
        regex=True,
        first=True,
    ).otp


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

        if response.status_code != 200:
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

    def auth(self) -> bool:
        try:
            url = el.LINK_AUTENTICACAO_SSO.format(regiao=self.regiao)
            self.driver.get(url)

            if "https://sso.cloud.pje.jus.br/" not in self.driver.current_url:
                return True

            path_certificado = Path(environ.get("CERTIFICADO_PFX"))
            senha_certificado = environ.get(
                "CERTIFICADO_PASSWORD",
            ).encode()
            autenticador = AutenticadorPJe(
                path_certificado,
                senha_certificado,
            )

            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.CSS_FORM_LOGIN,
                )),
            )

            autenticado = autenticador.autenticar()
            if not autenticado:
                raise

            desafio = autenticado[0]
            uuid_sessao = autenticado[1]

            self.driver.execute_script(
                el.COMMAND,
                el.ID_INPUT_DESAFIO,
                desafio,
            )
            self.driver.execute_script(
                el.COMMAND,
                el.ID_CODIGO_PJE,
                uuid_sessao,
            )

            self.driver.execute_script("document.forms[0].submit()")

            otp_uri = _get_otp_uri()
            otp = str(pyotp.parse_uri(uri=otp_uri).now())

            input_otp = WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[id="otp"]',
                )),
            )

            input_otp.send_keys(otp)
            input_otp.send_keys(Keys.ENTER)

            WebDriverWait(
                driver=self.driver,
                timeout=10,
                poll_frequency=0.3,
                ignored_exceptions=(UnexpectedAlertPresentException),
            ).until(ec.url_contains("pjekz"))

        except Exception:
            self.print_message(
                message="Erro ao realizar autenticação",
                message_type="error",
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
