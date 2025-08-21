"""Módulo para a classe de controle dos robôs PJe."""

from __future__ import annotations

import json.decoder
import secrets
import traceback
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from threading import Lock
from time import sleep
from typing import TYPE_CHECKING, ClassVar, Literal, cast

from dotenv import dotenv_values
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import (
    ExecutionError,
    FileUploadError,
)
from crawjud.common.exceptions.validacao import ValidacaoStringError
from crawjud.controllers.master import CrawJUD
from crawjud.interfaces.types import BotData
from crawjud.interfaces.types.custom import StrProcessoCNJ
from crawjud.interfaces.types.pje import (
    DictDesafio,
    DictResults,
    DictSeparaRegiao,
    Processo,
)
from crawjud.resources.elements import pje as el
from crawjud.utils.formatadores import formata_tempo
from crawjud.utils.iterators import RegioesIterator
from crawjud.utils.models.logs import CachedExecution
from crawjud.utils.recaptcha import captcha_to_image
from crawjud.utils.webdriver import DriverBot

if TYPE_CHECKING:
    from httpx import Client, Response

    from crawjud.custom.task import ContextTask
    from crawjud.interfaces.dict.bot import BotData

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()
environ = dotenv_values()
HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15


class PjeBot[T](CrawJUD):
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
        super().__init__(system="pje")
        start_time: datetime = formata_tempo(str(current_task.request.eta))

        self.folder_storage = storage_folder_name
        self.current_task = current_task
        self.start_time = start_time.strftime("%d/%m/%Y, %H:%M:%S")
        self.pid = str(current_task.request.id)

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

    def auth(self, regiao: str) -> bool:
        try:
            driver = DriverBot(
                selected_browser="chrome",
                with_proxy=True,
            )

            wait = driver.wait
            url_login = self.formata_url_pje(_format="login", regiao=regiao)
            url_valida_sessao = self.formata_url_pje(
                _format="validate_login",
                regiao=regiao,
            )

            driver.get(url_login)
            btn_sso = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'button[id="btnSsoPdpj"]',
                )),
            )
            btn_sso.click()

            sleep(5)

            btn_certificado = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ('div[class="certificado"] > a'),
                )),
            )
            event_cert = btn_certificado.get_attribute("onclick")
            driver.execute_script(event_cert)
            sleep(1)
            try:
                WebDriverWait(
                    driver=driver,
                    timeout=15,
                    poll_frequency=0.3,
                    ignored_exceptions=(UnexpectedAlertPresentException),
                ).until(ec.url_to_be(url_valida_sessao))
            except TimeoutException:
                if "pjekz" not in driver.current_url:
                    return False

            if (
                "pjekz/painel/usuario-externo" in driver.current_url
                or "pjekz" in driver.current_url
            ):
                driver.refresh()

            cookies_driver = driver.get_cookies()
            har_data_ = driver.current_har
            entries = list(har_data_.entries)
            entry_proxy = [
                item
                for item in entries
                if f"https://pje.trt{regiao}.jus.br/pje-comum-api/"
                in item.request.url
            ][-1]

            cookies_ = {
                str(cookie["name"]): str(cookie["value"])
                for cookie in cookies_driver
            }

            headers_ = {
                str(header["name"]): str(header["value"])
                for header in entry_proxy.request.headers
            }

            driver.quit()

            self._cookies = cookies_
            self._headers = headers_

        except Exception:
            self.print_msg("Erro ao realizar autenticação", type_log="error")
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

    def save_file_downloaded(
        self,
        file_name: str,
        response_data: Response,
        processo: str,
        row: int,
    ) -> None:
        """Envia o `arquivo baixado` no processo para o `storage`.

        Arguments:
            file_name (str): Nome do arquivo.
            response_data (Response): response da request httpx.
            processo (str): processo.
            row (int): row do loop.

        """
        try:
            path_temp = workdir.joinpath("temp", self.pid.upper())

            path_temp.mkdir(parents=True, exist_ok=True)

            sleep_time = secrets.randbelow(7) + 2
            sleep(sleep_time)

            chunk = 8 * 1024 * 1024
            file_path = path_temp.joinpath(file_name)
            # Salva arquivo em chunks no storage
            with file_path.open("wb") as f:
                for _bytes in response_data.iter_bytes(chunk):
                    sleep(0.5)
                    f.write(_bytes)

            with suppress(Exception):
                other_path_ = Path(environ["PATH_SRV"])
                with other_path_.joinpath(file_name).open("wb") as f:
                    for _bytes in response_data.iter_bytes(chunk):
                        sleep(0.5)
                        f.write(_bytes)

        except (FileUploadError, Exception) as e:
            str_exc = "\n".join(traceback.format_exception_only(e))
            message = "Não foi possível baixar o arquivo. " + str_exc
            self.print_msg(
                row=row,
                message=message,
                type_log="info",
            )

        finally:
            message = f"Arquivo do processo n.{processo} baixado com sucesso!"
            self.print_msg(
                row=row,
                message=message,
                type_log="info",
            )

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

    def desafio_captcha(
        self,
        row: int,
        data: BotData,
        id_processo: str,
        client: Client,
    ) -> DictResults:
        """Resolve o desafio captcha para acessar informações do processo no PJe.

        Returns:
            Resultados: Dicionário contendo headers, cookies e resultados do processo.

        Raises:
            ExecutionError: Caso não seja possível obter informações do processo
            após 15 tentativas.

        """
        count_try: int = 0
        response_desafio = None
        data_request: DictDesafio = {}

        def formata_data_result() -> DictDesafio:
            request_json = response_desafio.json()

            if isinstance(request_json, list):
                request_json = request_json[-1]

            return cast("DictDesafio", request_json)

        def args_desafio() -> tuple[str, str]:
            if count_try == 0:
                link = f"/captcha?idProcesso={id_processo}"

                nonlocal response_desafio
                response_desafio = client.get(url=link, timeout=60)

                nonlocal data_request
                data_request = formata_data_result()

            img = data_request.get("imagem")
            token_desafio = data_request.get("tokenDesafio")

            return img, token_desafio

        while count_try <= COUNT_TRYS:
            sleep(0.25)
            with suppress(Exception):
                img, token_desafio = args_desafio()
                text = captcha_to_image(img)

                link = (
                    f"/processos/{id_processo}"
                    f"?tokenDesafio={token_desafio}"
                    f"&resposta={text}"
                )
                response_desafio = client.get(url=link, timeout=60)

                sleep_time = secrets.randbelow(5) + 3

                if response_desafio.status_code == HTTP_STATUS_FORBIDDEN:
                    raise ExecutionError(
                        message="Erro ao obter informações do processo",
                    )

                data_request = response_desafio.json()
                imagem = data_request.get("imagem")

                if imagem:
                    count_try += 1
                    sleep(sleep_time)
                    continue

                msg = (
                    f"Processo {data['NUMERO_PROCESSO']} encontrado! "
                    "Salvando dados..."
                )
                self.print_msg(
                    message=msg,
                    row=row,
                    type_log="info",
                )

                captcha_token = response_desafio.headers.get(
                    "captchatoken",
                    "",
                )
                return DictResults(
                    id_processo=id_processo,
                    captchatoken=str(captcha_token),
                    text=text,
                    data_request=cast("Processo", data_request),
                )
            count_try += 1

        if count_try > COUNT_TRYS:
            self.print_msg(
                message="Erro ao obter informações do processo",
                row=row,
                type_log="info",
            )
            return None

        return None

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
                numero_processo = StrProcessoCNJ(item["NUMERO_PROCESSO"])

                regiao = numero_processo.tj
                # Atualiza o número do processo no item
                item["NUMERO_PROCESSO"] = str(numero_processo)
                # Adiciona a posição do processo na
                # lista original no dicionário de posições
                position_process[numero_processo] = len(position_process)

                # Caso a região não exista no dicionário, cria uma nova lista
                if not regioes_dict.get(regiao):
                    regioes_dict[regiao] = [item]
                    continue

                # Caso a região já exista, adiciona o item à lista correspondente
                regioes_dict[regiao].append(item)

            except ValidacaoStringError:
                continue

        return {"regioes": regioes_dict, "position_process": position_process}

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
