"""Executa o processamento da capa dos processos PJE.

Este módulo contém a classe Capa responsável por autenticar, enfileirar e
processar processos judiciais, além de realizar o download da cópia integral
dos processos e salvar os resultados no storage.

"""

import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress
from queue import Queue
from time import sleep

from httpx import Client, Response
from tqdm import tqdm

from app.interfaces import BotData
from app.interfaces._pje import (
    AssuntosProcessoPJeDict,
    AudienciaProcessoPjeDict,
    CapaProcessualPJeDict,
    PartesProcessoPJeDict,
    ProcessoJudicialDict,
    RepresentantePartesPJeDict,
)
from app.interfaces._pje import (
    DictResults as DictResults,
)
from app.interfaces._pje import audiencias as audiencias
from app.interfaces._pje.assuntos import AssuntoDict as AssuntoDict
from app.interfaces._pje.assuntos import ItemAssuntoDict
from app.interfaces._pje.audiencias import AudienciaDict
from app.interfaces._pje.partes import ParteDict, PartesJsonDict
from app.types import Dict as Dict
from bots.controller.pje import PjeBot
from bots.resources.elements import pje as el
from common.exceptions import (
    ExecutionError as ExecutionError,
)
from common.exceptions import (
    FileUploadError as FileUploadError,
)
from constants import WORKDIR as WORKDIR

SENTINELA = None


class Capa(PjeBot):
    """Gerencia autenticação, enfileiramento e processamento de processos PJE.

    Esta classe executa autenticação, enfileiramento, processamento e download
    da cópia integral dos processos judiciais no sistema PJE, salvando os
    resultados no armazenamento definido.

    """

    queue_files: Queue

    def execution(self) -> None:
        """Executa o fluxo principal de processamento da capa dos processos PJE.

        Args:
            name (str | None): Nome do bot.
            system (str | None): Sistema do bot.
            current_task (ContextTask): Tarefa atual do Celery.
            storage_folder_name (str): Nome da pasta de armazenamento.
            *args: Argumentos variáveis.
            **kwargs: Argumentos nomeados variáveis.

        """
        self.queue_files = Queue()
        self.to_add_processos = []
        self.to_add_audiencias = []
        self.to_add_assuntos = []
        self.to_add_partes = []
        self.to_add_representantes = []
        generator_regioes = self.regioes()
        lista_nova = list(generator_regioes)

        self.total_rows = len(self.posicoes_processos)

        for regiao, data_regiao in lista_nova:
            self.regiao = regiao
            if self.bot_stopped.is_set():
                break

            if not self.auth():
                continue
            self.queue_regiao(data=data_regiao)

        self.finalize_execution()

    def queue_regiao(self, data: list[BotData]) -> None:
        headers, cookies = self.get_headers_cookies()
        client_context = Client(cookies=cookies, headers=headers)
        executor = ThreadPoolExecutor(16)

        with client_context as client, executor as pool:
            futures: list[Future[None]] = []

            for item in data:
                futures.append(
                    pool.submit(self.queue, item=item, client=client)
                )
                sleep(1.5)
            _results = [future.result() for future in futures]

    def queue(self, item: BotData, client: Client) -> None:
        if not self.bot_stopped.is_set():
            sleep(0.5)
            row = int(self.posicoes_processos[item["NUMERO_PROCESSO"]] + 1)
            processo = item["NUMERO_PROCESSO"]
            try:
                resultados = self.search(data=item, row=row, client=client)
                if resultados:
                    self.print_message(
                        message="Processo encontrado!",
                        message_type="info",
                        row=row,
                    )

                    capa = self.capa_processual(
                        result=resultados["data_request"]
                    )
                    sleep(0.5)
                    partes, assuntos, audiencias, representantes = (
                        self.outras_informacoes(
                            processo=processo,
                            client=client,
                            id_processo=resultados["id_processo"],
                        )
                    )

                    for to_save, sheet_name in [
                        ([capa], "Capa"),
                        (audiencias, "Audiências"),
                        (assuntos, "Assuntos"),
                        (partes, "Partes"),
                        (representantes, "Representantes"),
                    ]:
                        self.append_success(
                            work_sheet=sheet_name, data_save=to_save
                        )

                    message_type = "success"
                    message = "Execução Efetuada com sucesso!"
                    self.print_message(
                        message=message,
                        message_type=message_type,
                        row=row,
                    )

            except Exception as e:
                exc = "\n".join(traceback.format_exception(e))
                tqdm.write(exc)
                self.print_message(
                    message="Erro ao extrair informações do processo",
                    message_type="error",
                    row=row,
                )

    def outras_informacoes(
        self,
        processo: str,
        client: Client,
        id_processo: str,
    ) -> tuple[
        list[PartesProcessoPJeDict],
        list[AssuntosProcessoPJeDict],
        list[AudienciaProcessoPjeDict],
        list[RepresentantePartesPJeDict],
    ]:
        request_partes: Response = None
        request_assuntos: Response = None
        request_audiencias: Response = None

        data_partes: list[PartesProcessoPJeDict] = []
        data_assuntos: list[AssuntosProcessoPJeDict] = []
        data_audiencias: list[AudienciaProcessoPjeDict] = []
        data_representantes: list[RepresentantePartesPJeDict] = []

        link_partes = el.LINK_CONSULTA_PARTES.format(
            trt_id=self.regiao,
            id_processo=id_processo,
        )
        link_assuntos = el.LINK_CONSULTA_ASSUNTOS.format(
            trt_id=self.regiao,
            id_processo=id_processo,
        )
        link_audiencias = el.LINK_AUDIENCIAS.format(
            trt_id=self.regiao,
            id_processo=id_processo,
        )

        sleep(0.25)
        with suppress(Exception):
            request_partes = client.get(url=link_partes)
            if request_partes:
                data_partes, data_representantes = self._salva_partes(
                    processo=processo,
                    data_partes=request_partes.json(),
                )

        sleep(0.25)
        with suppress(Exception):
            request_assuntos = client.get(url=link_assuntos)
            if request_assuntos:
                data_assuntos = self._salva_assuntos(
                    processo=processo,
                    data_assuntos=request_assuntos.json(),
                )

        sleep(0.25)
        with suppress(Exception):
            request_audiencias = client.get(url=link_audiencias)
            if request_audiencias:
                data_audiencias = self._salva_audiencias(
                    processo=processo,
                    data_audiencia=request_audiencias.json(),
                )

        return data_partes, data_assuntos, data_audiencias, data_representantes

    def _salva_audiencias(
        self, processo: str, data_audiencia: list[AudienciaDict]
    ) -> list[AudienciaProcessoPjeDict]:
        return [
            AudienciaProcessoPjeDict(
                ID_PJE=audiencia["id"],
                processo=processo,
                TIPO_AUDIENCIA=audiencia["tipo"]["descricao"],
                MODO_AUDIENCIA="PRESENCIAL"
                if audiencia["tipo"]["isVirtual"]
                else "VIRTUAL",
                STATUS=audiencia["status"],
                DATA_INICIO=audiencia.get("dataInicio"),
                DATA_FIM=audiencia.get("dataFim"),
                DATA_MARCACAO=audiencia.get("dataMarcacao"),
            )
            for audiencia in data_audiencia
        ]

    def _salva_assuntos(
        self,
        processo: str,
        data_assuntos: list[ItemAssuntoDict],
    ) -> list[AssuntosProcessoPJeDict]:
        return [
            AssuntosProcessoPJeDict(
                ID_PJE=assunto["id"],
                PROCESSO=processo,
                ASSUNTO_COMPLETO=assunto["assunto"]["assuntoCompleto"],
                ASSUNTO_RESUMIDO=assunto["assunto"]["assuntoResumido"],
            )
            for assunto in data_assuntos
        ]

    def _salva_partes(
        self,
        processo: str,
        data_partes: PartesJsonDict,
    ) -> tuple[list[PartesProcessoPJeDict], list[RepresentantePartesPJeDict]]:
        partes: list[PartesProcessoPJeDict] = []
        representantes: list[RepresentantePartesPJeDict] = []
        for v in data_partes.values():
            list_partes_request: list[ParteDict] = v

            for parte in list_partes_request:
                partes.append(
                    PartesProcessoPJeDict(
                        ID_PJE=parte.get("id"),
                        NOME=parte.get("nome"),
                        DOCUMENTO=parte.get("documento", "000.000.000-00"),
                        TIPO_DOCUMENTO=parte.get(
                            "tipoDocumento",
                            "Não Informado",
                        ),
                        TIPO_PARTE=parte.get("polo"),
                        TIPO_PESSOA="Física"
                        if parte.get("tipoPessoa", "f").lower() == "f"
                        else "Jurídica",
                        PROCESSO=processo,
                        POLO=parte.get("polo"),
                        PARTE_PRINCIPAL=parte.get("principal", False),
                    ),
                )

                if "representantes" in parte:
                    representantes.extend(
                        [
                            RepresentantePartesPJeDict(
                                ID_PJE=representante.get("id", ""),
                                PROCESSO=processo,
                                NOME=representante.get("nome", ""),
                                DOCUMENTO=representante.get(
                                    "documento",
                                    "",
                                ),
                                TIPO_DOCUMENTO=representante.get(
                                    "tipoDocumento",
                                    "",
                                ),
                                REPRESENTADO=parte["nome"],
                                TIPO_PARTE=representante["polo"],
                                TIPO_PESSOA=representante["tipoPessoa"],
                                POLO=representante["polo"],
                                OAB=representante.get("numeroOab", "0000"),
                                EMAILS=",".join(
                                    representante.get("emails", []),
                                ),
                                TELEFONE=f"({representante.get('dddCelular')}) {representante.get('numeroCelular')}"
                                if "dddCelular" in representante
                                and "numeroCelular" in representante
                                else "",
                            )
                            for representante in parte["representantes"]
                        ],
                    )

        return partes, representantes

    def capa_processual(
        self, result: ProcessoJudicialDict
    ) -> CapaProcessualPJeDict:
        link_consulta = f"https://pje.trt{self.regiao}.jus.br/pjekz/processo/{result['id']}/detalhe"
        return CapaProcessualPJeDict(
            ID_PJE=result["id"],
            LINK_CONSULTA=link_consulta,
            processo=result["numero"],
            CLASSE=result["classeJudicial"]["descricao"],
            SIGLA_CLASSE=result["classeJudicial"]["sigla"],
            ORGAO_JULGADOR=result["orgaoJulgador"]["descricao"],
            SIGLA_ORGAO_JULGADOR=result["orgaoJulgador"]["sigla"],
            DATA_DISTRIBUICAO=result.get("distribuidoEm", ""),
            STATUS_PROCESSO=result["labelStatusProcesso"],
            SEGREDO_JUSTIÇA=result["segredoDeJustica"],
            VALOR_CAUSA=result["valorDaCausa"],
        )
