"""Gerencie o protocolo de petições no sistema JusBr de forma automatizada.

Este módulo contém a classe Protocolo, responsável por executar o fluxo de
protocolo de petições judiciais utilizando automação com Selenium, incluindo
seleção de tipo de protocolo, upload de documentos e tratamento de erros.

"""

import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress

import dotenv
from httpx import Client

from bots.pje.protocolo.habilitacao import HabilitiacaoPJe

dotenv.load_dotenv()


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

            headers, cookies = self.get_headers_cookies(regiao=regiao)

            self._headers = headers
            self._cookies = cookies

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
        client_context = Client(cookies=self.cookies)
        with client_context as client:
            for data in data_regiao:
                try:
                    if self.event_stop_bot.is_set():
                        return

                    row = self.posicoes_processos[data["NUMERO_PROCESSO"]] + 1
                    self.row = row
                    tipo_protocolo = data["TIPO_PROTOCOLO"]

                    if "habilitação" in tipo_protocolo.lower():
                        self.protocolar_habilitacao(
                            bot_data=data,
                            regiao=regiao,
                        )

                    else:
                        _d = self.search(
                            data=data,
                            row=row,
                            regiao=regiao,
                            client=client,
                        )

                    self.print_msg(
                        "Protocolo efetuado com sucesso!",
                        row=row,
                        type_log="success",
                    )

                except (KeyError, Exception) as e:
                    exc_message = "\n".join(traceback.format_exception_only(e))

                    self.print_msg(
                        message=f"Erro ao protocolar processo. Erro: {exc_message}",
                        type_log="error",
                        row=row,
                    )
