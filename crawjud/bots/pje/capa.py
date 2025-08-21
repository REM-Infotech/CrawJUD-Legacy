"""Executa o processamento da capa dos processos PJE.

Este módulo contém a classe Capa responsável por autenticar, enfileirar e
processar processos judiciais, além de realizar o download da cópia integral
dos processos e salvar os resultados no storage.

"""

from __future__ import annotations

import secrets  # noqa: F401
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from threading import Semaphore, Thread
from time import sleep
from typing import TYPE_CHECKING, ClassVar, TypedDict

from dotenv import load_dotenv
from httpx import Client, ReadError
from pandas import DataFrame, ExcelWriter
from tqdm import tqdm

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.pje import PjeBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls
from crawjud.resources.elements import pje as el
from crawjud.utils.formatadores import formata_tempo

if TYPE_CHECKING:
    from datetime import datetime

    from crawjud.interfaces.pje import ProcessoJudicialDict
    from crawjud.interfaces.types import BotData
    from crawjud.interfaces.types.pje import (
        DictResults,  # noqa: F401
    )
load_dotenv()


class DictSalvarPlanilha(TypedDict):
    """Defina o dicionário para salvar dados da planilha de processos PJE.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        LINK_CONSULTA (str): URL para consulta do processo.
        NUMERO_PROCESSO (str): Número do processo judicial.
        CLASSE (str): Classe judicial do processo.
        SIGLA_CLASSE (str): Sigla da classe judicial.
        DATA_DISTRIBUICAO (datetime): Data de distribuição do processo.
        STATUS_PROCESSO (str): Status atual do processo.
        SEGREDO_JUSTIÇA (str): Indica se o processo está em segredo de justiça.

    Returns:
        DictSalvarPlanilha: Dicionário tipado com os dados do processo.

    """

    ID_PJE: int
    LINK_CONSULTA: str
    NUMERO_PROCESSO: str
    CLASSE: str
    SIGLA_CLASSE: str
    ORGAO_JULGADOR: str
    SIGLA_ORGAO_JULGADOR: str
    DATA_DISTRIBUICAO: datetime
    STATUS_PROCESSO: str
    SEGREDO_JUSTIÇA: str


@shared_task(name="pje.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa(PjeBot):
    """Gerencia autenticação, enfileiramento e processamento de processos PJE.

    Esta classe executa autenticação, enfileiramento, processamento e download
    da cópia integral dos processos judiciais no sistema PJE, salvando os
    resultados no armazenamento definido.

    """

    semaforo_arquivo: Semaphore = Semaphore(5)
    semaforo_processo: Semaphore = Semaphore(5)
    threads_processos: ClassVar[list[Thread]] = []
    threads_download_file: ClassVar[list[Thread]] = []

    to_save: ClassVar[list[DictSalvarPlanilha]] = []

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
        nome_planilha = f"Planilha Resultados - {self.pid}.xlsx"
        self.path_planilha = self.output_dir_path.joinpath(nome_planilha)
        with ExcelWriter(
            path=self.path_planilha,
            mode="w",
            engine="openpyxl",
        ) as writer:
            DataFrame().to_excel(
                excel_writer=writer,
                sheet_name="Resultados",
                index=False,
            )

        generator_regioes = self.regioes()
        for regiao, data_regiao in generator_regioes:
            with suppress(Exception):
                self.print_msg(message=f"Autenticando no TRT {regiao}")
                if self.auth():
                    self.print_msg(
                        message="Autenticado com sucesso!",
                        type_log="info",
                    )
                    self.queue_processo(data=data_regiao)

    def queue_processo(self, data: list[BotData]) -> str:
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
        client_context = Client(cookies=self.cookies, headers=self.headers)
        pool_exe = ThreadPoolExecutor(max_workers=6)
        with client_context as client, pool_exe as executor:
            futures = [
                executor.submit(self.thread_processo, item=item, client=client)
                for item in data
            ]
            for future in as_completed(futures):
                with suppress(Exception):
                    future.result()

            self.save_results()

            for th in self.threads_download_file:
                with suppress(Exception):
                    th.join()

    def thread_processo(self, item: BotData, client: Client) -> None:
        with self.semaforo_processo:
            try:
                sleep(0.5)
                processo = item["NUMERO_PROCESSO"]
                row = self.posicoes_processos[item["NUMERO_PROCESSO"]] + 1
                resultados = self.search(data=item, row=row, client=client)
                self.formatar_resultado(result=resultados["data_request"])

                if item.get("TRAZER_COPIA", "N").lower() == "s":
                    file_name = f"CÓPIA INTEGRAL - {processo} - {self.pid}.pdf"
                    thread_download_file = Thread(
                        target=self.copia_integral,
                        kwargs={
                            "file_name": file_name,
                            "row": row,
                            "client": client,
                            "processo": processo,
                            "id_processo": resultados["id_processo"],
                        },
                    )
                    sleep(0.5)
                    thread_download_file.start()
                    self.threads_download_file.append(thread_download_file)

                self.print_msg(
                    message="Execução Efetuada com sucesso!",
                    row=row,
                    type_log="success",
                )

                sleep(0.5)

            except Exception as e:
                tqdm.write("\n".join(traceback.format_exception(e)))

    def formatar_resultado(self, result: ProcessoJudicialDict) -> None:
        """Formata o resultado da busca para armazenar na planilha."""
        link_consulta = f"https://pje.trt{self.regiao}.jus.br/pjekz/processo/{result['id']}/detalhe"

        dict_salvar_planilha = DictSalvarPlanilha(
            ID_PJE=result["id"],
            LINK_CONSULTA=link_consulta,
            NUMERO_PROCESSO=result["numero"],
            CLASSE=result["classeJudicial"]["descricao"],
            SIGLA_CLASSE=result["classeJudicial"]["sigla"],
            ORGAO_JULGADOR=result["orgaoJulgador"]["descricao"],
            SIGLA_ORGAO_JULGADOR=result["orgaoJulgador"]["sigla"],
            DATA_DISTRIBUICAO=formata_tempo(result["distribuidoEm"]),
            STATUS_PROCESSO=result["labelStatusProcesso"],
            SEGREDO_JUSTIÇA=result["segredoDeJustica"],
            VALOR_CAUSA=result["valorDaCausa"],
        )

        self.to_save.append(dict_salvar_planilha)

    def save_results(self) -> None:
        xlsx_writer = ExcelWriter(
            path=self.path_planilha,
            mode="a",
            engine="openpyxl",
            if_sheet_exists="overlay",
        )

        with xlsx_writer as writer:
            dataframe = DataFrame(self.to_save)

            # Remove timezone dos campos datetime para evitar erro do Excel
            for col in dataframe.select_dtypes(include=["datetimetz"]).columns:
                dataframe[col] = dataframe[col].dt.tz_localize(None)

            dataframe.to_excel(
                excel_writer=writer,
                sheet_name="Resultados",
                index=False,
            )

        self.to_save.clear()

    def copia_integral(
        self,
        file_name: str,
        row: int,
        processo: str,
        client: Client,
        id_processo: str,
    ) -> None:
        """Realiza o download da cópia integral do processo e salva no storage.

        Args:
            client (Client): httx client.
            processo (str): processo.
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
        with self.semaforo_arquivo:
            try:
                sleep(0.50)
                headers = client.headers
                cookies = client.cookies

                client = Client(
                    timeout=900,
                    headers=headers,
                    cookies=cookies,
                )
                sleep(0.50)
                link = el.LINK_DOWNLOAD_INTEGRA.format(
                    trt_id=self.regiao,
                    id_processo=id_processo,
                )
                message = f"Baixando arquivo do processo n.{processo}"
                sleep(0.50)
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
                            processo=processo,
                            row=row,
                        )

                sleep(0.50)
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
