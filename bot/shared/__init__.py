from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Type, Union

from dotenv import load_dotenv
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

# from memory_profiler import profile


Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = Dict[str, Union[TypeValues, Numbers]]

# fp = open("memory_profiler_self.log", "+w")

load_dotenv()

TypeHint = Union[List[str | Numbers | SubDict] | SubDict]


class BasePropertiesCrawJUD:

    def __init__(self, *args, **kwrgs) -> None:
        """Base class for all scripts"""

    appends_ = []
    another_append_ = []
    path_args_: Type[str] = ""
    path_accepted_: Type[str] = ""
    vara_: Type[str] = ""
    _system: Type[str] = ""
    _state_or_client_: Type[str] = ""
    _type_log: Type[str] = "info"
    _message: Type[str] = ""
    _pid: Type[str] = ""
    kwrgs_: Dict[str, Union[TypeValues, SubDict]] = {}
    row_: int = 0
    message_error_: Type[str] = ""
    bot_data_: Dict[str, Union[TypeValues, SubDict]] = {}
    graphicMode_: Type[str] = "doughnut"
    out_dir: Type[str] = ""
    user_data_dir: Type[str] = ""
    cr_list_args: list[str] = []
    drv: WebDriver = None
    wt: WebDriverWait = None
    elmnt = None
    interact_ = None
    path_: Path = None

    @property
    def path(self) -> Path:
        return self.path_

    @path.setter
    def path(self, new_path: Path):

        if not isinstance(new_path, Path):
            raise ValueError("Path must be a Path object")

        self.path_ = new_path

    @property
    def path_args(self) -> str:
        return self.path_args_

    @path_args.setter
    def path_args(self, new_path: Type[str]):
        self.path_args_ = new_path

    @property
    # @profile(stream=fp)
    def appends(self):
        return self.appends_

    @appends.setter
    # @profile(stream=fp)
    def appends(self, new_appends: list):
        self.appends_ = new_appends

    @property
    # @profile(stream=fp)
    def another_append(self):
        return self.another_append_

    @another_append.setter
    # @profile(stream=fp)
    def another_append(self, new_another_append: list):
        self.another_append_ = new_another_append

    @property
    # @profile(stream=fp)
    def system(self) -> str:
        return self._system

    @system.setter
    # @profile(stream=fp)
    def system(self, system_: Type[str]):
        self._system = system_

    @property
    # @profile(stream=fp)
    def state_or_client(self):
        return self._state_or_client_

    @state_or_client.setter
    # @profile(stream=fp)
    def state_or_client(self, new_s: Type[str]):
        self._state_or_client_ = new_s

    @property
    # @profile(stream=fp)
    def type_log(self):
        return self._type_log

    @type_log.setter
    # @profile(stream=fp)
    def type_log(self, new_log: Type[str]):
        self._type_log = new_log

    @property
    # @profile(stream=fp)
    def pid(self) -> int:
        return self._pid

    @pid.setter
    # @profile(stream=fp)
    def pid(self, pid_) -> int:
        self._pid = pid_

    @property
    # @profile(stream=fp)
    def message(self) -> str:
        return self._message

    @message.setter
    # @profile(stream=fp)
    def message(self, new_msg: Type[str]) -> str:
        self._message = new_msg

    @property
    # @profile(stream=fp)
    def isStoped(self):
        chk = os.path.exists(os.path.join(self.output_dir_path, f"{self.pid}.flag"))
        return chk

    @property
    # @profile(stream=fp)
    def driver(self) -> WebDriver:  # pragma: no cover
        return self.drv

    @driver.setter
    # @profile(stream=fp)
    def driver(self, new_drv: WebDriver):  # pragma: no cover
        self.drv = new_drv

    @property
    # @profile(stream=fp)
    def wait(self) -> WebDriverWait:  # pragma: no cover
        return self.wt

    @wait.setter
    # @profile(stream=fp)
    def wait(self, new_wt: WebDriverWait):  # pragma: no cover
        self.wt = new_wt

    @property
    # @profile(stream=fp)
    def chr_dir(self):
        return self.user_data_dir

    @chr_dir.setter
    # @profile(stream=fp)
    def chr_dir(self, new_dir: Type[str]):
        self.user_data_dir = new_dir

    @property
    # @profile(stream=fp)
    def output_dir_path(self):
        return self.out_dir

    @output_dir_path.setter
    # @profile(stream=fp)
    def output_dir_path(self, new_outdir: Type[str]):
        self.out_dir = new_outdir

    @property
    # @profile(stream=fp)
    def kwrgs(self) -> dict:
        return self.kwrgs_

    @kwrgs.setter
    # @profile(stream=fp)
    def kwrgs(self, new_kwg: Dict[str, Any]):
        self.kwrgs_ = new_kwg

        for key, value in list(new_kwg.items()):
            setattr(self, key, value)

    @property
    # @profile(stream=fp)
    def row(self) -> int:
        return self.row_

    @row.setter
    # @profile(stream=fp)
    def row(self, new_row: int):
        self.row_ = new_row

    @property
    # @profile(stream=fp)
    def message_error(self) -> str:
        return self.message_error_

    @message_error.setter
    # @profile(stream=fp)
    def message_error(self, nw_m: Type[str]) -> str:
        self.message_error_ = nw_m

    @property
    # @profile(stream=fp)
    def graphicMode(self) -> str:
        return self.graphicMode_

    @graphicMode.setter
    # @profile(stream=fp)
    def graphicMode(self, new_graph):
        self.graphicMode_ = new_graph

    @property
    # @profile(stream=fp)
    def list_args(self):  # pragma: no cover
        return [
            "--ignore-ssl-errors=yes",
            "--ignore-certificate-errors",
            "--display=:99",
            "--window-size=1600,900",
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--kiosk-printing",
        ]

    @list_args.setter
    # @profile(stream=fp)
    def list_args(self, new_Args: list[str]):  # pragma: no cover
        self.cr_list_args = new_Args

    @property
    # @profile(stream=fp)
    def bot_data(self) -> dict[str, str | Numbers]:
        return self.bot_data_

    @bot_data.setter
    # @profile(stream=fp)
    def bot_data(self, new_botdata: dict[str, str | Numbers]):
        self.bot_data_ = new_botdata

    @property
    # @profile(stream=fp)
    def vara(self) -> str:  # pragma: no cover
        return self.vara_

    @vara.setter
    # @profile(stream=fp)
    def vara(self, vara_str: Type[str]):
        self.vara_ = vara_str

    @property
    # @profile(stream=fp)
    def path_accepted(self):
        return self.path_accepted_

    @path_accepted.setter
    # @profile(stream=fp)
    def path_accepted(self, new_path: Type[str]):
        self.path_accepted_ = new_path

    @property
    def nomes_colunas(self) -> List[str]:

        all_fields = [
            "NOME_PARTE",
            "PORTAL",
            "FORO",
            "CLASSE",
            "NOME_INTERESSADO",
            "CPF_CNPJ_AUTOR",
            "CPF_CNPJ_REU",
            "VIA_CONDENACAO",
            "TIPO_INTERESSADO",
            "PRAZO_PGTO",
            "AUTOR",
            "REU",
            "TRIBUNAL",
            "COMARCA",
            "VARA",
            "AGENCIA",
            "TIPO_ACAO",
            "VALOR_CALCULADO",
            "TEXTO_DESC",
            "DATA_PGTO",
            "NOME_CUSTOM",
            "TIPO_PROTOCOLO",
            "SUBTIPO_PROTOCOLO",
            "TIPO_ARQUIVO",
            "PETICAO_PRINCIPAL",
            "ANEXOS",
            "TIPO_ANEXOS",
            "TIPO_BUSCA",
            "TERMOS",
            "DATA_FILTRO",
            "QTD_SEQUENCIA",
            "NUMERO_PROCESSO",
            "AREA_DIREITO",
            "SUBAREA_DIREITO",
            "ESTADO",
            "DATA_DISTRIBUICAO",
            "PARTE_CONTRARIA",
            "TIPO_PARTE_CONTRARIA",
            "DOC_PARTE_CONTRARIA",
            "EMPRESA",
            "TIPO_EMPRESA",
            "DOC_EMPRESA",
            "UNIDADE_CONSUMIDORA",
            "CAPITAL_INTERIOR",
            "DIVISAO",
            "ACAO",
            "DATA_CITACAO",
            "OBJETO",
            "PROVIMENTO",
            "ADVOGADO_INTERNO",
            "ADV_PARTE_CONTRARIA",
            "FATO_GERADOR",
            "ESCRITORIO_EXTERNO",
            "VALOR_CAUSA",
            "FASE",
            "PROVISAO",
            "DATA_ATUALIZACAO",
            "VALOR_ATUALIZACAO",
            "OBSERVACAO",
            "TIPO_ANDAMENTO",
            "DATA",
            "OCORRENCIA",
            "OBSERVACAO",
            "ANEXOS",
            "TIPO_ANEXOS",
            "TIPO_GUIA",
            "VALOR_GUIA",
            "DATA_LANCAMENTO",
            "TIPO_PAGAMENTO",
            "SOLICITANTE",
            "TIPO_CONDENACAO",
            "COD_BARRAS",
            "DOC_GUIA",
            "DOC_CALCULO",
            "LOCALIZACAO",
            "CNPJ_FAVORECIDO",
            "PARTE_PETICIONANTE",
            "GRAU",
            "DATA_PUBLICACAO",
            "PALAVRA_CHAVE",
            "TRAZER_DOC",
            "INTIMADO",
            "TRAZER_TEOR",
            "DATA_LIMITE",
            "NOME_MOV",
            "CIDADE_ESTADO",
            "ESFERA",
            "REQUERENTE",
            "REQUERIDO",
            "JUROS_PARTIR",
            "DATA_INCIDENCIA",
            "VALOR_CALCULO",
            "DATA_CALCULO",
            "MULTA_PERCENTUAL",
            "MULTA_DATA",
            "MULTA_VALOR",
            "PERCENT_MULTA_475J",
            "HONORARIO_SUCUMB_PERCENT",
            "HONORARIO_SUCUMB_DATA",
            "HONORARIO_SUCUMB_VALOR",
            "HONORARIO_SUCUMB_PARTIR",
            "JUROS_PERCENT",
            "HONORARIO_CUMPRIMENTO_PERCENT",
            "HONORARIO_CUMPRIMENTO_DATA",
            "HONORARIO_CUMPRIMENTO_VALOR",
            "HONORARIO_CUMPRIMENTO_PARTIR",
            "CUSTAS_DATA",
            "CUSTAS_VALOR",
            "DESC_PAGAMENTO",
            "DESC_OBJETO",
        ]
        return all_fields


class PropertiesCrawJUD(BasePropertiesCrawJUD):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__dict__.update(kwargs)
        self.kwrgs = kwargs

    def __getattr__(self, nome: Type[str]) -> TypeHint:
        super_cls = super()
        item = self.kwrgs.get(nome, None)

        if not item:
            item = getattr(super_cls, nome, None)

        return item
