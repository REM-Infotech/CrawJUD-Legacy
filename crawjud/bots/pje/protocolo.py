"""Executa o processamento da Protocolo dos processos PJE.

Este módulo contém a classe Protocolo responsável por autenticar, enfileirar e
processar processos judiciais, além de realizar o download da cópia integral
dos processos e salvar os resultados no storage.

"""

from __future__ import annotations

import secrets  # noqa: F401
import traceback
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    as_completed,
)
from contextlib import suppress
from threading import Semaphore
from time import sleep
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from httpx import Client
from tqdm import tqdm

from crawjud.controllers.pje import PjeBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls

if TYPE_CHECKING:
    from crawjud.interfaces.types import BotData

load_dotenv()

SENTINELA = None

semaforo_arquivo: Semaphore = Semaphore(10)
semaforo_processo: Semaphore = Semaphore(10)


@shared_task(name="pje.protocolo", bind=True, base=ContextTask)
@wrap_cls
class Protocolo(PjeBot):
    """Gerencia autenticação, enfileiramento e processamento de processos PJE.

    Esta classe executa autenticação, enfileiramento, processamento e download
    da cópia integral dos processos judiciais no sistema PJE, salvando os
    resultados no armazenamento definido.

    """

    def execution(self) -> None:
        """Executa o fluxo principal de processamento da Protocolo dos processos PJE.

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

        with ThreadPoolExecutor(max_workers=8) as executor:
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

        for to_save, sheet_name in [
            (self.to_add_processos, "Protocolo"),
            (self.to_add_audiencias, "Audiências"),
            (self.to_add_assuntos, "Assuntos"),
            (self.to_add_partes, "Partes"),
            (self.to_add_representantes, "Representantes"),
        ]:
            self.queue_save_xlsx.put({
                "to_save": to_save,
                "sheet_name": sheet_name,
            })

        with suppress(Exception):
            self.queue_save_xlsx.join()

        with suppress(Exception):
            self.queue_files.join()

        with suppress(Exception):
            self.queue_msg.join()

        self.event_queue_files.set()
        self.event_queue_save_xlsx.set()
        self.finalize_execution()

    def queue_regiao(self, regiao: str, data_regiao: list[BotData]) -> None:
        try:
            if self.event_stop_bot.is_set():
                return

            self.print_msg(message=f"Autenticando no TRT {regiao}")
            autenticar = self.auth(regiao=regiao)
            if autenticar:
                self.print_msg(
                    message="Autenticado com sucesso!",
                    type_log="info",
                )
                self.queue_processo(data=data_regiao, regiao=regiao)

        except Exception as e:
            self.print_msg(
                message="\n".join(traceback.format_exception(e)),
                type_log="info",
            )

    def queue_processo(self, data: list[BotData], regiao: str) -> str:
        """Enfileira processos para processamento e salva resultados.

        Args:
            regiao (str): regiao
            data (list[BotData]): Lista de dados dos processos.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.

        """
        client_context = Client(cookies=self.cookies, headers=self.headers)
        pool_exe = ThreadPoolExecutor(max_workers=16)
        with client_context as client, pool_exe as executor:
            futures: list[Future] = []
            for item in data:
                futures.append(
                    executor.submit(
                        self.queue,
                        item=item,
                        client=client,
                        regiao=regiao,
                    ),
                )
                sleep(3)

            for future in as_completed(futures):
                with suppress(Exception):
                    future.result()

    def queue(
        self,
        item: BotData,
        client: Client,
        regiao: str,
    ) -> None:
        try:
            if self.event_stop_bot.is_set():
                return

            self.print_msg(
                message="Execução Efetuada com sucesso!",
                row=self.row,
                type_log="success",
            )

        except Exception as e:
            tqdm.write("\n".join(traceback.format_exception(e)))
            self.print_msg(
                message="Erro ao extrair informações do processo",
                type_log="error",
                row=self.row,
            )
