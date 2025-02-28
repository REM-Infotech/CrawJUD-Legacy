"""Utility module: Provide various helpers for legal process tasks; handle data, certs, and logs instantly.

This module aggregates several utility classes and functions used across the application.
It includes authentication, browser control, file handling, and data processing routines.
"""

import logging
import os
import re
import ssl
import subprocess  # nosec: B404
import time
import traceback
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Union

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from pandas import Timestamp
from werkzeug.utils import secure_filename

from ..common import ExecutionError
from ..core import CrawJUD, pd
from crawjud.bot.shared import Numbers
from .auth import AuthBot
from .Driver import DriverBot
from .elements import ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM, ElementsBot
from .interator import Interact
from .MakeTemplate import MakeXlsx
from .PrintLogs import PrintBot, SendMessage
from .search import SearchBot

__all__ = [
    "ELAW_AME",
    "ESAJ_AM",
    "PJE_AM",
    "PROJUDI_AM",
    "AuthBot",
    "DriverBot",
    "ElementsBot",
    "Interact",
    "MakeXlsx",
    "PrintBot",
    "SearchBot",
    "SendMessage",
]

TypeData = Union[list[dict[str, Union[str, Numbers, datetime]]], dict[str, Union[str, Numbers, datetime]]]

logger = logging.getLogger(__name__)


class OtherUtils(CrawJUD):
    """Perform various data processing and interaction functions for CrawJUD-Bots.

    This class offers methods for data formatting, logging, certificate installation,
    and other common tasks used across the legal process systems.
    """

    def __init__(self) -> None:
        """Initialize OtherUtils instance.

        Set up any attributes and configurations for subsequent utility operations.
        """

    @property
    def nomes_colunas(self) -> list[str]:
        """Return a list of column names used in legal process spreadsheets.

        Returns:
            list[str]: A list containing all the required column labels.

        """
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

    @property
    def elaw_data(self) -> dict[str, str]:
        """Return a dict with keys for legal case details and empty string values.

        Returns:
            dict[str, str]: Keys mapped to empty strings for default legal data.

        """
        return {
            "NUMERO_PROCESSO": "",
            "AREA_DIREITO": "",
            "SUBAREA_DIREITO": "",
            "ESTADO": "",
            "COMARCA": "",
            "FORO": "",
            "VARA": "",
            "DATA_DISTRIBUICAO": "",
            "PARTE_CONTRARIA": "",
            "TIPO_PARTE_CONTRARIA": "",
            "DOC_PARTE_CONTRARIA": "",
            "EMPRESA": "",
            "TIPO_EMPRESA": "",
            "DOC_EMPRESA": "",
            "UNIDADE_CONSUMIDORA": "",
            "CAPITAL_INTERIOR": "",
            "DIVISAO": "",
            "ACAO": "",
            "DATA_CITACAO": "",
            "OBJETO": "",
            "PROVIMENTO": "",
            "ADVOGADO_INTERNO": "",
            "ADV_PARTE_CONTRARIA": "",
            "FATO_GERADOR": "",
            "ESCRITORIO_EXTERNO": "",
            "VALOR_CAUSA": "",
            "FASE": "",
        }

    @property
    def cities_Amazonas(self) -> dict[str, str]:  # noqa: N802
        """Return a dictionary categorizing Amazonas cities as 'Capital' or 'Interior'.

        Returns:
            dict[str, str]: City names with associated regional classification.

        """
        return {
            "Alvarães": "Interior",
            "Amaturá": "Interior",
            "Anamã": "Interior",
            "Anori": "Interior",
            "Apuí": "Interior",
            "Atalaia do Norte": "Interior",
            "Autazes": "Interior",
            "Barcelos": "Interior",
            "Barreirinha": "Interior",
            "Benjamin Constant": "Interior",
            "Beruri": "Interior",
            "Boa Vista do Ramos": "Interior",
            "Boca do Acre": "Interior",
            "Borba": "Interior",
            "Caapiranga": "Interior",
            "Canutama": "Interior",
            "Carauari": "Interior",
            "Careiro": "Interior",
            "Careiro da Várzea": "Interior",
            "Coari": "Interior",
            "Codajás": "Interior",
            "Eirunepé": "Interior",
            "Envira": "Interior",
            "Fonte Boa": "Interior",
            "Guajará": "Interior",
            "Humaitá": "Interior",
            "Ipixuna": "Interior",
            "Iranduba": "Interior",
            "Itacoatiara": "Interior",
            "Itamarati": "Interior",
            "Itapiranga": "Interior",
            "Japurá": "Interior",
            "Juruá": "Interior",
            "Jutaí": "Interior",
            "Lábrea": "Interior",
            "Manacapuru": "Interior",
            "Manaquiri": "Interior",
            "Manaus": "Capital",
            "Manicoré": "Interior",
            "Maraã": "Interior",
            "Maués": "Interior",
            "Nhamundá": "Interior",
            "Nova Olinda do Norte": "Interior",
            "Novo Airão": "Interior",
            "Novo Aripuanã": "Interior",
            "Parintins": "Interior",
            "Pauini": "Interior",
            "Presidente Figueiredo": "Interior",
            "Rio Preto da Eva": "Interior",
            "Santa Isabel do Rio Negro": "Interior",
            "Santo Antônio do Içá": "Interior",
            "São Gabriel da Cachoeira": "Interior",
            "São Paulo de Olivença": "Interior",
            "São Sebastião do Uatumã": "Interior",
            "Silves": "Interior",
            "Tabatinga": "Interior",
            "Tapauá": "Interior",
            "Tefé": "Interior",
            "Tonantins": "Interior",
            "Uarini": "Interior",
            "Urucará": "Interior",
            "Urucurituba": "Interior",
        }

    def dataFrame(self) -> list[dict[str, str]]:  # noqa: N802
        """Convert an Excel file to a list of dictionaries with formatted data.

        Reads an Excel file, processes the data by formatting dates and floats,
        and returns the data as a list of dictionaries.

        Returns:
            list[dict[str, str]]: A record list from the processed Excel file.

        Raises:
            FileNotFoundError: If the target file does not exist.
            ValueError: For problems reading the file.

        """
        input_file = Path(self.output_dir_path).joinpath(self.xlsx).resolve()

        df = pd.read_excel(input_file)
        df.columns = df.columns.str.upper()

        for col in df.columns:
            df[col] = df[col].apply(lambda x: (x.strftime("%d/%m/%Y") if isinstance(x, (datetime, Timestamp)) else x))

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(lambda x: f"{x:.2f}".replace(".", ","))

        vars_df = []

        df_dicted = df.to_dict(orient="records")
        for item in df_dicted:
            for key, value in item.items():
                if str(value) == "nan":
                    item[key] = None
            vars_df.append(item)

        return vars_df

    def elawFormats(self, data: dict[str, str]) -> dict[str, str]:  # noqa: N802
        """Format a legal case dictionary according to pre-defined rules.

        Args:
            data (dict[str, str]): The raw data dictionary.

        Returns:
            dict[str, str]: The data formatted with proper types and values.

        Rules:
            - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
            - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
            - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
            - If the value is an integer or float, format it to two decimal places and replace the decimal point with a clcomma.
            - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".

        """  # noqa: E501
        data_listed = list(data.items())
        for key, value in data_listed:
            if isinstance(value, str):
                if not value.strip():
                    data.pop(key)

            elif value is None:
                data.pop(key)

            if key.upper() == "TIPO_EMPRESA":
                data["TIPO_PARTE_CONTRARIA"] = "Autor"
                if value.upper() == "RÉU":
                    data["TIPO_PARTE_CONTRARIA"] = "Autor"

            elif key.upper() == "COMARCA":
                set_locale = self.cities_Amazonas.get(value, "Outro Estado")
                data["CAPITAL_INTERIOR"] = set_locale

            elif key == "DATA_LIMITE" and not data.get("DATA_INICIO"):
                data["DATA_INICIO"] = value

            elif isinstance(value, (int, float)):
                data[key] = f"{value:.2f}".replace(".", ",")

            elif key == "CNPJ_FAVORECIDO" and not value:
                data["CNPJ_FAVORECIDO"] = "04.812.509/0001-90"

        return data

    def calc_time(self) -> list[int]:
        """Calculate and return elapsed time as minutes and seconds.

        Returns:
            list[int]: A two-item list: [minutes, seconds] elapsed.

        """
        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        minutes = int(execution_time / 60)
        seconds = int(execution_time - minutes * 60)
        return [minutes, seconds]

    def append_moves(self) -> None:
        """Append legal movement records to the spreadsheet if any exist.

        Raises:
            ExecutionError: If no movements are available to append.

        """
        if self.appends:
            for append in self.appends:
                self.append_success(append, "Movimentação salva na planilha com sucesso!!")
        else:
            raise ExecutionError("Nenhuma Movimentação encontrada")

    def append_success(
        self,
        data: TypeData,
        message: str = None,
        fileN: str = None,  # noqa: N803
    ) -> None:
        """Append successful execution data to the success spreadsheet.

        Args:
            data (TypeData): The data to be appended.
            message (str, optional): A success message to log.
            fileN (str, optional): Filename override for saving data.

        """
        if not message:
            message = "Execução do processo efetuada com sucesso!"

        def save_info(data: list[dict[str, str]]) -> None:
            output_success = self.path

            if fileN or not output_success:
                output_success = Path(self.path).parent.resolve().joinpath(fileN)

            if not output_success.exists():
                df = pd.DataFrame(data)
            else:
                df_existing = pd.read_excel(output_success)
                df = df_existing.to_dict(orient="records")
                df.extend(data)

            new_data = pd.DataFrame(df)
            new_data.to_excel(output_success, index=False)

        typed = type(data) is list and all(isinstance(item, dict) for item in data)

        if not typed:
            data2 = dict.fromkeys(self.name_colunas, "")
            for item in data:
                data2_itens = list(filter(lambda x: x[1] is None or x[1].strip() == "", list(data2.items())))
                for key, _ in data2_itens:
                    data2.update({key: item})
                    break

            data.clear()
            data.append(data2)

        save_info(data)

        if message:
            if self.type_log == "log":
                self.type_log = "success"

            self.message = message
            self.prt()

    def append_error(self, data: dict[str, str] = None) -> None:
        """Append error information to the error spreadsheet file.

        Args:
            data (dict[str, str], optional): The error record to log.

        """
        if not os.path.exists(self.path_erro):
            df = pd.DataFrame([data])
        else:
            df_existing = pd.read_excel(self.path_erro)
            df = df_existing.to_dict(orient="records")
            df.extend([data])

        new_data = pd.DataFrame(df)
        new_data.to_excel(self.path_erro, index=False)

    def append_validarcampos(self, data: list[dict[str, str]]) -> None:
        """Append validated field records to the validation spreadsheet.

        Args:
            data (list[dict[str, str]]): The list of validated data dictionaries.

        """
        nomeplanilha = f"CAMPOS VALIDADOS PID {self.pid}.xlsx"
        planilha_validar = Path(self.path).parent.resolve().joinpath(nomeplanilha)
        if not os.path.exists(planilha_validar):
            df = pd.DataFrame(data)
        else:
            df_existing = pd.read_excel(planilha_validar)
            df = df_existing.to_dict(orient="records")
            df.extend(data)

        new_data = pd.DataFrame(df)
        new_data.to_excel(planilha_validar, index=False)

    def count_doc(self, doc: str) -> Union[str, None]:
        """Determine whether a document number is CPF or CNPJ based on character length.

        Args:
            doc (str): The document number as string.

        Returns:
            Union[str, None]: 'cpf', 'cnpj', or None if invalid.

        """
        numero = "".join(filter(str.isdigit, doc))
        if len(numero) == 11:
            return "cpf"
        if len(numero) == 14:
            return "cnpj"
        return None

    def get_recent(self, folder: str) -> Union[str, None]:
        """Return the most recent PDF file path from a folder.

        Args:
            folder (str): The directory to search.

        Returns:
            Union[str, None]: Full path to the most recent PDF file, or None.

        """
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if (os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(".pdf"))
            and not f.lower().endswith(".crdownload")  # W261, W503
        ]
        files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        return files[0] if files else None

    def format_string(self, string: str) -> str:
        """Return a secure, normalized filename based on the input string.

        Args:
            string (str): The original filename.

        Returns:
            str: A secure version of the filename.

        """
        return secure_filename(
            "".join([c for c in unicodedata.normalize("NFKD", string) if not unicodedata.combining(c)]),
        )

    def normalizar_nome(self, word: str) -> str:
        """Normalize a word by removing spaces and special separators.

        Args:
            word (str): The input word.

        Returns:
            str: The normalized, lowercase word.

        """
        return re.sub(r"[\s_\-]", "", word).lower()

    def similaridade(
        self,
        word1: str,
        word2: str,
    ) -> float:
        """Compare two words and return their similarity ratio.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            float: A ratio where 1.0 denotes an identical match.

        """
        return SequenceMatcher(None, word1, word2).ratio()

    def finalize_execution(self) -> None:
        """Finalize bot execution by closing browsers and logging total time.

        Performs cookie cleanup, quits the driver, and prints summary logs.
        """
        window_handles = self.driver.window_handles
        self.row += 1
        if window_handles:
            self.driver.delete_all_cookies()
            self.driver.quit()

        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        minutes, seconds = divmod(int(execution_time), 60)
        self.prt(status="Finalizado")

        self.type_log = "success"
        self.message = f"Fim da execução, tempo: {minutes} minutos e {seconds} segundos"
        self.prt()

    def install_cert(self) -> None:
        """Install a certificate if it is not already installed.

        Uses certutil to import the certificate and logs the operation.
        """

        def CertIsInstall(crt_sbj_nm: str, store: str = "MY") -> bool:  # noqa: N802
            for cert, _, _ in ssl.enum_certificates(store):
                try:
                    x509_cert = x509.load_der_x509_certificate(cert, default_backend())
                    subject_name = x509_cert.subject.rfc4514_string()
                    if crt_sbj_nm in subject_name:
                        return True
                except Exception:
                    err = traceback.format_exc()
                    logger.exception(err)

            return False

        installed = CertIsInstall(self.name_cert.split(".pfx")[0])

        if not installed:
            path_cert = os.path.join(self.output_dir_path, self.name_cert)
            comando = ["certutil", "-importpfx", "-user", "-f", "-p", self.token, "-silent", path_cert]
            try:
                resultado = subprocess.run(  # nosec: B603
                    comando,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.message = resultado.stdout
                self.type_log = "log"
                self.prt()
            except subprocess.CalledProcessError as e:
                raise e

    def group_date_all(
        self,
        data: dict[str, dict[str, str]],
    ) -> list[dict[str, str]]:
        """Group legal case records by date and vara and return a list of records.

        Args:
            data (dict[str, dict[str, str]]): Data grouped by vara and date.

        Returns:
            list[dict[str, str]]: Flattened record list including dates and vara.

        """
        records = []
        for vara, dates in data.items():
            for date, entries in dates.items():
                for entry in entries:
                    record = {"Data": date, "Vara": vara}
                    record.update(entry)
                    records.append(record)
        return records

    def group_keys(
        self,
        data: list[dict[str, str]],
    ) -> dict[str, dict[str, str]]:
        """Group keys from a list of dictionaries into a consolidated mapping.

        Args:
            data (list[dict[str, str]]): List of dictionaries with process data.

        Returns:
            dict[str, dict[str, str]]: A dictionary mapping keys to value dictionaries.

        """
        record = {}
        for pos, entry in enumerate(data):
            for key, value in entry.items():
                if key not in record:
                    record[key] = {}
                record[key][str(pos)] = value
        return record

    def gpt_chat(self, text_mov: str) -> str:
        """Obtain an adjusted description via GPT chat based on the legal document text.

        Args:
            text_mov (str): The legal document text for analysis.

        Returns:
            str: An adjusted response derived from GPT chat.

        """
        try:
            time.sleep(5)
            client = self.OpenAI_client
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.headgpt},
                    {
                        "role": "user",
                        "content": (
                            f"Analise o seguinte texto e ajuste sua resposta de acordo com o tipo de documento: {text_mov}."  # noqa: E501
                        ),
                    },
                ],
                temperature=0.1,
                max_tokens=300,
            )

            choices = completion.choices
            choice = choices[0]
            choice_message = choice.message
            text = choice_message.content

            return text or text_mov

        except Exception as e:
            raise e

    def text_is_a_date(self, text: str) -> bool:
        """Determine if the provided text matches a date-like pattern.

        Args:
            text (str): The text to evaluate.

        Returns:
            bool: True if the text resembles a date; False otherwise.

        """
        date_like_pattern = r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"
        return bool(re.search(date_like_pattern, text))
