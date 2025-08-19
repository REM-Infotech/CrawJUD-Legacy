"""Executa o processamento da capa dos processos PJE.

Este módulo contém a classe Capa responsável por autenticar, enfileirar e
processar processos judiciais, além de realizar o download da cópia integral
dos processos e salvar os resultados no storage.

"""

from __future__ import annotations

import secrets
import traceback
from contextlib import suppress
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, ClassVar

from dotenv import load_dotenv
from httpx import Client, ReadError

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.pje import PjeBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls

if TYPE_CHECKING:
    from concurrent.futures import Future

    from crawjud.interfaces.types import BotData
    from crawjud.interfaces.types.pje import DictResults
load_dotenv()


@shared_task(name="pje.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa(PjeBot):
    """Gerencia autenticação, enfileiramento e processamento de processos PJE.

    Esta classe executa autenticação, enfileiramento, processamento e download
    da cópia integral dos processos judiciais no sistema PJE, salvando os
    resultados no armazenamento definido.

    """

    tasks_queue_processos: ClassVar[list[Future]] = []

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
        for regiao, data_regiao in generator_regioes:
            with suppress(Exception):
                self.print_msg(message=f"Autenticando no TRT {regiao}")
                if self.auth():
                    self.print_msg(
                        message="Autenticado com sucesso!",
                        type_log="info",
                    )
                    self.queue_processo(
                        data=data_regiao,
                        base_url=self.base_url,
                        headers=self.headers,
                        cookies=self.cookies,
                    )

            self.print_msg(
                message="Erro de execução",
                type_log="error",
            )

    def queue_processo(
        self,
        data: list[BotData],
        base_url: str,
        headers: str,
        cookies: str,
    ) -> str:
        """Enfileira processos para processamento e salva resultados.

        Args:
            cookies (dict[str, str]): Cookies de autenticação.
            headers (dict[str, str]): Cabeçalhos HTTP.
            base_url (str): URL base do serviço.
            data (list[BotData]): Lista de dados dos processos.
            pid (str): Identificador do processo.
            start_time (str): Horário de início do processamento.
            position_process (dict[str, int]): Posições dos processos.
            total_rows (int): Total de linhas a processar.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.



        """
        client = Client(
            base_url=base_url,
            timeout=30,
            headers=headers,
            cookies=cookies,
            follow_redirects=True,
        )

        thread_download_file: list[Thread] = []

        for item in data:
            sleep_time = secrets.randbelow(7) + 2
            sleep(sleep_time)
            try:
                # Atualiza dados do item para processamento
                row = self.list_posicao_processo[item["NUMERO_PROCESSO"]] + 1
                resultado: DictResults = self.search(
                    data=item,
                    row=row,
                    client=client,
                )

                if resultado:
                    data_request = resultado.get("data_request")
                    if data_request:
                        # Salva dados em cache
                        self.save_success_cache(
                            data=data_request,
                            processo=item["NUMERO_PROCESSO"],
                        )

                        thread_file_ = Thread(
                            target=self.copia_integral,
                            kwargs={
                                "row": row,
                                "data": item,
                                "client": client,
                                "id_processo": resultado["id_processo"],
                                "captchatoken": resultado["captchatoken"],
                            },
                        )

                        thread_file_.start()
                        thread_download_file.append(thread_file_)

                        part_1_msg = (
                            "Informações do processo {numproc} ".format(
                                numproc=item["NUMERO_PROCESSO"],
                            )
                        )

                        part_2_msg = "salvas com sucesso!"
                        message = f"{part_1_msg}{part_2_msg}"
                        self.print_msg(
                            message=message,
                            row=row,
                            type_log="success",
                        )

                else:
                    self.print_msg(
                        message="Processo não encontrado!",
                        row=row,
                        type_log="error",
                    )
            except ExecutionError:
                self.print_msg(
                    message="Erro ao buscar processo",
                    row=row,
                    type_log="error",
                )

        for th in thread_download_file:
            with suppress(Exception):
                th.join()

    def copia_integral(
        self,
        row: int,
        data: BotData,
        client: Client,
        id_processo: str,
        captchatoken: str,
    ) -> None:
        """Realiza o download da cópia integral do processo e salva no storage.

        Args:
            client (Client): httx client.
            data (BotData): bot data.
            row (int): current row.
            pid: str: Identificador do processo.
            url_base (str): URL base do serviço.
            headers (dict[str, str]): Cabeçalhos HTTP.
            cookies (dict[str, str]): Cookies de autenticação.
            id_processo (str): Identificador do processo.
            captchatoken (str): Token do captcha.
            file_name (str): Nome do arquivo para salvar.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.



        """
        try:
            base_url = client.base_url
            headers = client.headers
            cookies = client.cookies

            client = Client(
                base_url=base_url,
                timeout=30,
                headers=headers,
                cookies=cookies,
            )
            file_name = (
                f"COPIA INTEGRAL {data['NUMERO_PROCESSO']} {self.pid}.pdf"
            )
            proc = data["NUMERO_PROCESSO"]
            id_proc = id_processo
            captcha = captchatoken
            link = f"/processos/{id_proc}/integra?tokenCaptcha={captcha}"
            message = f"Baixando arquivo do processo n.{proc}"
            self.print_msg(
                message=message,
                row=row,
                type_log="log",
            )

            def call_stream() -> None:
                with client.stream("get", url=link) as response:
                    self.save_file_downloaded(
                        file_name=file_name,
                        response_data=response,
                        data_bot=data,
                        row=row,
                    )

            try:
                call_stream()

            except ReadError:
                call_stream()

        except ExecutionError as e:
            self.print_msg(
                message="\n".join(traceback.format_exception(e)),
                row=self.row,
                type_log="info",
            )

            msg = "Erro ao baixar arquivo"

            self.print_msg(message=msg, row=row, type_log="info")
