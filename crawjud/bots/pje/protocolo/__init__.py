"""Gerencie o protocolo de petições no sistema JusBr de forma automatizada.

Este módulo contém a classe Protocolo, responsável por executar o fluxo de
protocolo de petições judiciais utilizando automação com Selenium, incluindo
seleção de tipo de protocolo, upload de documentos e tratamento de erros.

"""

from __future__ import annotations

import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

import dotenv
from httpx import Client
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.bots.pje.protocolo.habilitacao import HabilitiacaoPJe
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls

if TYPE_CHECKING:
    from crawjud.interfaces.dict.bot import BotData

dotenv.load_dotenv()


@shared_task(name="pje.protocolo", bind=True, base=ContextTask)
@wrap_cls
class Protocolo(HabilitiacaoPJe):
    """Gerencia o protocolo de petições no sistema JusBr."""

    def execution(self) -> None:
        """Executa o fluxo principal de processamento da capa dos processos PJE.

        Args:
            name (str | None): Nome do bot.
            system (str | None): Sistema do bot.
            current_task (ContextTask): Tarefa atual do Celery.
            storage_folder_name (str): Nome da pasta de armazenamento.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.

        """
        generator_regioes = self.regioes()
        lista_nova = list(generator_regioes)

        with ThreadPoolExecutor(max_workers=1) as executor:
            futures: list[Future] = []
            for regiao, data_regiao in lista_nova:
                if self.event_stop_bot.is_set():
                    break

                futures.append(
                    executor.submit(
                        self.queue_regiao,
                        regiao=regiao,
                        data_regiao=data_regiao,
                    ),
                )
                sleep(30)

            for future in futures:
                with suppress(Exception):
                    future.result()

        self.finalize_execution()

    def queue_regiao(self, regiao: str, data_regiao: list[BotData]) -> None:
        try:
            if self.event_stop_bot.is_set():
                return

            _grau_text = {
                "1": "primeirograu",
                "2": "segundograu",
            }

            url = f"https://pje.trt{regiao}.jus.br/primeirograu/authenticateSSO.seam"
            self.driver.get(url)

            cookies_driver = self.driver.get_cookies()
            self._cookies = {
                str(cookie["name"]): str(cookie["value"])
                for cookie in cookies_driver
            }

            self.queue(
                data_regiao=data_regiao,
                regiao=regiao,
            )

        except Exception as e:
            self.print_msg(
                message="\n".join(traceback.format_exception(e)),
                type_log="info",
            )

    def queue(
        self,
        data_regiao: list[BotData],
        regiao: str,
    ) -> None:
        try:
            client_context = Client(cookies=self.cookies)

            with client_context as client:
                _wait2 = WebDriverWait(self.driver, 10)
                for data in data_regiao:
                    if self.event_stop_bot.is_set():
                        return

                    row = self.posicoes_processos[data["NUMERO_PROCESSO"]] + 1
                    _d = self.search(
                        data=data,
                        row=row,
                        regiao=regiao,
                        client=client,
                    )

                    sleep(5)

                    tipo_protocolo = data["TIPO_PROTOCOLO"]

                    if "habilitação" in tipo_protocolo.lower():
                        self.protocolar_habilitacao(
                            bot_data=data,
                            regiao=regiao,
                        )

                    self.print_msg(
                        message="Execução Efetuada com sucesso!",
                        row=row,
                        type_log="success",
                    )

        except Exception:
            self.print_msg(
                message="Erro ao extrair informações do processo",
                type_log="error",
                row=row,
            )
