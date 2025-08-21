"""Executa o processamento da capa dos processos PJE.

Este módulo contém a classe Capa responsável por autenticar, enfileirar e
processar processos judiciais, além de realizar o download da cópia integral
dos processos e salvar os resultados no storage.

"""

from __future__ import annotations

import secrets  # noqa: F401
import traceback
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from contextlib import suppress
from queue import Queue
from threading import Semaphore, Thread
from time import sleep
from typing import TYPE_CHECKING, ClassVar

from dotenv import load_dotenv
from httpx import Client
from pandas import DataFrame, ExcelWriter
from tqdm import tqdm

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.pje import PjeBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls
from crawjud.interfaces.pje import DictSalvarPlanilha
from crawjud.resources.elements import pje as el
from crawjud.utils.formatadores import formata_tempo

if TYPE_CHECKING:
    from pathlib import Path

    from crawjud.interfaces.pje import ProcessoJudicialDict
    from crawjud.interfaces.types import BotData
    from crawjud.interfaces.types.pje import DictResults

load_dotenv()


queue_files = Queue()
queue_save_xlsx = Queue()
semaforo_arquivo: Semaphore = Semaphore(10)
semaforo_processo: Semaphore = Semaphore(10)


@shared_task(name="pje.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa(PjeBot):
    """Gerencia autenticação, enfileiramento e processamento de processos PJE.

    Esta classe executa autenticação, enfileiramento, processamento e download
    da cópia integral dos processos judiciais no sistema PJE, salvando os
    resultados no armazenamento definido.

    """

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
        Thread(target=copia_integral, daemon=True).start()
        Thread(
            target=save_file,
            kwargs={"output_dir_path": self.output_dir_path, "pid": self.pid},
            daemon=True,
        ).start()
        generator_regioes = self.regioes()

        futures: list[Future] = []

        with ThreadPoolExecutor(max_workers=1) as executor:
            for regiao, data_regiao in generator_regioes:
                futures.append([
                    executor.submit(
                        self.queue,
                        regiao=regiao,
                        data_regiao=data_regiao,
                    ),
                ])

            for future in futures:
                with suppress(Exception):
                    future.result()

    def queue(self, regiao: str, data_regiao: list[BotData]) -> None:
        try:
            self.print_msg(message=f"Autenticando no TRT {regiao}")
            autenticar = self.auth()
            if autenticar:
                self.print_msg(
                    message="Autenticado com sucesso!",
                    type_log="info",
                )
                self.queue_processo(data=data_regiao)

        except Exception as e:
            self.print_msg(
                message="\n".join(traceback.format_exception(e)),
                type_log="info",
            )

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
        pool_exe = ThreadPoolExecutor(max_workers=8)
        with client_context as client, pool_exe as executor:
            futures = [
                executor.submit(self.thread_processo, item=item, client=client)
                for item in data
            ]
            for future in as_completed(futures):
                with suppress(Exception):
                    future.result()

            with suppress(Exception):
                queue_files.join()

    def thread_processo(self, item: BotData, client: Client) -> None:
        try:
            sleep(0.5)
            processo = item["NUMERO_PROCESSO"]
            row = self.posicoes_processos[item["NUMERO_PROCESSO"]] + 1
            resultados: DictResults = self.search(
                data=item,
                row=row,
                client=client,
            )

            if not isinstance(resultados, dict):
                self.print_msg(
                    message=str(resultados),
                    type_log="error",
                )
                return

            self.formatar_resultado(result=resultados["data_request"])

            if item.get("TRAZER_COPIA", "N").lower() == "s":
                file_name = f"CÓPIA INTEGRAL - {processo} - {self.pid}.pdf"
                queue_files.put({
                    "self": self,
                    "file_name": file_name,
                    "row": row,
                    "client": client,
                    "processo": processo,
                    "id_processo": resultados["id_processo"],
                })
                sleep(0.5)

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

        queue_save_xlsx.put({"to_save": [dict_salvar_planilha]})


def save_file(output_dir_path: Path, pid: str) -> None:
    """Salve resultados em planilha Excel e atualize conforme dados enfileirados.

    Args:
        output_dir_path (Path): Caminho do diretório de saída para salvar a planilha.
        pid (str): Identificador do processo para nomear o arquivo Excel.

    """
    nome_planilha = f"Planilha Resultados - {pid}.xlsx"
    path_planilha = output_dir_path.joinpath(nome_planilha)
    with ExcelWriter(
        path=path_planilha,
        mode="w",
        engine="openpyxl",
    ) as writer:
        DataFrame().to_excel(
            excel_writer=writer,
            sheet_name="Resultados",
            index=False,
        )

    while True:
        data = queue_save_xlsx.get()

        if data:
            try:
                data = dict(data)
                to_save: list[DictSalvarPlanilha] = data.get("to_save")

                xlsx_writer = ExcelWriter(
                    path=path_planilha,
                    mode="a",
                    engine="openpyxl",
                    if_sheet_exists="overlay",
                )

                with xlsx_writer as writer:
                    dataframe = DataFrame(to_save)

                    # Remove timezone dos campos datetime para evitar erro do Excel
                    for col in dataframe.select_dtypes(
                        include=["datetimetz"],
                    ).columns:
                        dataframe[col] = dataframe[col].dt.tz_localize(None)

                    dataframe.to_excel(
                        excel_writer=writer,
                        sheet_name="Resultados",
                        index=False,
                    )

            except Exception as e:
                tqdm.write("\n".join(traceback.format_exception(e)))


def copia_integral() -> None:
    """Realiza o download da cópia integral do processo e salva no storage."""
    while True:
        data = queue_files.get()

        if data:
            data = dict(data)
            sel: Capa = data.get("self")
            file_name: str = data.get("file_name")
            row: int = data.get("row")
            processo: str = data.get("processo")
            client: Client = data.get("client")
            id_processo: str = data.get("id_processo")

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
                    trt_id=sel.regiao,
                    id_processo=id_processo,
                )
                message = f"Baixando arquivo do processo n.{processo}"
                sleep(0.50)
                sel.print_msg(
                    message=message,
                    row=row,
                    type_log="log",
                )

                with client.stream("get", url=link) as response:
                    sel.save_file_downloaded(
                        file_name=file_name,
                        response_data=response,
                        processo=processo,
                        row=row,
                    )

            except ExecutionError as e:
                sel.print_msg(
                    message="\n".join(traceback.format_exception(e)),
                    row=sel.row,
                    type_log="info",
                )

                msg = "Erro ao baixar arquivo"
                sel.print_msg(message=msg, row=row, type_log="info")
