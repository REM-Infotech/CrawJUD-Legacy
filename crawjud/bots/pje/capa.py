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
from crawjud.utils.pje_savexlsx import SavePjeXlsx

if TYPE_CHECKING:
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

    tasks_queue_processos: ClassVar[list[Thread]] = []
    thread_download_file: ClassVar[list[Thread]] = []

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

                continue

            self.print_msg(
                message="Erro de execução",
                type_log="error",
            )

        self.print_msg(
            "Fim da execução! Salvando resultados na planilha...",
            type_log="info",
        )
        nome_planilha = f"Resultados Busca - {self.pid[:6]}.xlsx"
        path_planilha = self.output_dir_path.joinpath(nome_planilha)
        xlsx = SavePjeXlsx(path_planilha=path_planilha, pid=self.pid)
        xlsx.save()
        self.print_msg("Resultados salvos com sucesso!", type_log="success")

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
        for item in data:
            if len(self.tasks_queue_processos) == 5:
                for th in self.tasks_queue_processos:
                    th.join()

                self.tasks_queue_processos.clear()

            thread_proc = Thread(
                target=self.thread_search_proc,
                kwargs={
                    "base_url": base_url,
                    "headers": headers,
                    "cookies": cookies,
                    "item": item,
                },
            )

            sleep(3)
            thread_proc.start()
            self.tasks_queue_processos.append(thread_proc)

        for th in self.tasks_queue_processos:
            with suppress(Exception):
                th.join()
                sleep_time = secrets.randbelow(7) + 2
                sleep(sleep_time)

        for th in self.thread_download_file:
            with suppress(Exception):
                th.join()

    def thread_search_proc(
        self,
        base_url: str,
        headers: dict,
        cookies: dict,
        item: BotData,
    ) -> None:
        try:
            client = Client(
                base_url=base_url,
                timeout=30,
                headers=headers,
                cookies=cookies,
                follow_redirects=True,
            )

            # Atualiza dados do item para processamento
            row = self.list_posicao_processo[item["NUMERO_PROCESSO"]] + 1
            sleep(1)
            resultado: DictResults = self.search(
                data=item,
                row=row,
                client=client,
            )
            sleep(1)
            if resultado:
                sleep(1)
                data_request = resultado.get("data_request")
                if data_request:
                    # Salva dados em cache
                    sleep(1)
                    self.save_success_cache(
                        data=data_request,
                        processo=item["NUMERO_PROCESSO"],
                    )
                    file_name = f"COPIA INTEGRAL {item['NUMERO_PROCESSO']} {self.pid}.pdf"
                    thread_file_ = Thread(
                        target=self.copia_integral,
                        kwargs={
                            "file_name": file_name,
                            "row": row,
                            "data": item,
                            "client": client,
                            "id_processo": resultado["id_processo"],
                            "captchatoken": resultado["captchatoken"],
                        },
                    )
                    sleep(1)
                    thread_file_.start()
                    self.thread_download_file.append(thread_file_)

                    part_1_msg = "Informações do processo {numproc} ".format(
                        numproc=item["NUMERO_PROCESSO"],
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

    def copia_integral(
        self,
        file_name: str,
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
            sleep(1)
            base_url = client.base_url
            headers = client.headers
            cookies = client.cookies

            client = Client(
                base_url=base_url,
                timeout=600,
                headers=headers,
                cookies=cookies,
            )
            sleep(1)
            proc = data["NUMERO_PROCESSO"]
            id_proc = id_processo
            captcha = captchatoken
            link = f"/processos/{id_proc}/integra?tokenCaptcha={captcha}"
            message = f"Baixando arquivo do processo n.{proc}"
            sleep(1)
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

            sleep(1)
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
