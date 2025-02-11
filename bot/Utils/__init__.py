"""Utility module for CrawJUD-Bots, providing various classes and functions.

for authentication, driving browsers, interacting with elements, and more.

Classes:
    OtherUtils: Provides utility methods for data processing and interaction.
"""

import logging
import os
import re
import ssl
import subprocess  # nosec: B404 # noqa: S404
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
from ..shared import Numbers
from .auth import AuthBot
from .Driver import DriverBot
from .elements import ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM, ElementsBot
from .interator import Interact
from .MakeTemplate import MakeXlsx
from .PrintLogs import PrintBot
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
]

TypeData = Union[list[dict[str, Union[str, Numbers, datetime]]], dict[str, Union[str, Numbers, datetime]]]

logger = logging.getLogger(__name__)


class OtherUtils(CrawJUD):
    """Provides utility methods for data processing and interaction within CrawJUD-Bots.

    Methods:
        nomes_colunas() -> list[str]
        elaw_data() -> dict[str, str]
        cities_Amazonas() -> dict[str, str]
        dataFrame() -> list[dict[str, str]]
        elawFormats(data: dict[str, str]) -> dict[str, str]
        calc_time() -> list[int]
        append_moves() -> None
        append_success(data: TypeData, message: str = None, fileN: str = None) -> None
        append_error(data: dict[str, str] = None) -> None
        append_validarcampos(data: list[dict[str, str]]) -> None
        count_doc(doc: str) -> Union[str, None]
        get_recent(folder: str) -> Union[str, None]
        format_string(string: str) -> str
        normalizar_nome(word: str) -> str
        similaridade(word1: str, word2: str) -> float
        finalize_execution() -> None
        install_cert() -> None
        group_date_all(data: dict[str, dict[str, str]]) -> list[dict[str, str]]
        group_keys(data: list[dict[str, str]]) -> dict[str, dict[str, str]]
        gpt_chat(text_mov: str) -> str
        text_is_a_date(text: str) -> bool

    """

    def __init__(self) -> None:
        """Initialize the OtherUtils instance.

        Sets up necessary attributes and configurations for utility operations.
        """

    @property
    def nomes_colunas(self) -> list[str]:
        """Retrieve a list of column names.

        Returns:
            list[str]: A list of column names used in the application.

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
        """Generate a dictionary with keys related to legal case information and empty string values.

        Returns:
            dict[str, str]: A dictionary containing keys for legal case details with empty string values.

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
        """Return a dictionary of cities in the state of Amazonas, Brazil, categorized as either "Capital" or "Interior".

        Returns:
            dict[str, str]: A dictionary where the keys are city names and the values are their categories.

        """  # noqa: E501
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
            list[dict[str, str]]: A list of dictionaries representing each row in the Excel file.

        Raises:
            FileNotFoundError: If the specified Excel file does not exist.
            ValueError: If there is an issue reading the Excel file.

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

    def elawFormats(self, data: dict[str, str]) -> dict[str, str]:  # noqa: N802, C901
        """Format the given data dictionary according to specific rules.

        Args:
            data (dict[str, str]): A dictionary containing key-value pairs to be formatted.

        Returns:
            dict[str, str]: The formatted dictionary.

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
        """Calculate the elapsed time since the start time and return it as a list of minutes and seconds.

        Returns:
            list[int]: A list containing two integers:
                - minutes (int): The number of minutes of the elapsed time.
                - seconds (int): The number of seconds of the elapsed time.

        """
        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        minutes = int(execution_time / 60)
        seconds = int(execution_time - minutes * 60)
        return [minutes, seconds]

    def append_moves(self) -> None:
        """Append movements to the spreadsheet if there are any movements to append.

        Checks if there are any movements stored in the `self.appends` list.
        If there are, iterates over each movement and calls the `self.append_success`
        method to save the movement to the spreadsheet with a success message.

        Raises:
            ExecutionError: If no movements are found in the `self.appends` list.

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
        """Append successful execution data to the spreadsheet.

        Args:
            data (TypeData): The data to append.
            message (str, optional): Success message. Defaults to None.
            fileN (str, optional): Filename to save data. Defaults to None.

        Raises:
            ValueError: If data is not in the expected format.

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
        """Append error data to the error spreadsheet.

        Args:
            data (dict[str, str], optional): The error data to append. Defaults to None.

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
        """Append validated fields to the spreadsheet.

        Args:
            data (list[dict[str, str]]): The validated data to append.

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
        """Determine the type of Brazilian document based on its length.

        Args:
            doc (str): The document number as a string.

        Returns:
            Union[str, None]: The type of document ("cpf" or "cnpj") or None if invalid.

        """
        numero = "".join(filter(str.isdigit, doc))
        if len(numero) == 11:
            return "cpf"
        if len(numero) == 14:
            return "cnpj"
        return None

    def get_recent(self, folder: str) -> Union[str, None]:
        """Get the most recent PDF file from a specified folder.

        Args:
            folder (str): The path to the folder to search for PDF files.

        Returns:
            Union[str, None]: The path to the most recent PDF file, or None if none found.

        """
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if (os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(".pdf"))
            and not f.lower().endswith(".crdownload")  # noqa: W261, W503
        ]
        files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        return files[0] if files else None

    def format_string(self, string: str) -> str:
        """Format a given string to a secure filename.

        Args:
            string (str): The input string to be formatted.

        Returns:
            str: The formatted string as a secure filename.

        """
        return secure_filename(
            "".join([c for c in unicodedata.normalize("NFKD", string) if not unicodedata.combining(c)]),
        )

    def normalizar_nome(self, word: str) -> str:
        """Return a normalized version of the given word.

        Removes spaces, replaces "_" and "-" with nothing, and converts to lowercase.

        Args:
            word (str): The word to be normalized.

        Returns:
            str: The normalized name.

        """
        return re.sub(r"[\s_\-]", "", word).lower()

    def similaridade(self, word1: str, word2: str) -> float:
        """Compare similarity between two words.

        Args:
            word1 (str): First word.
            word2 (str): Second word.

        Returns:
            float: Percentage of similarity.

        """
        return SequenceMatcher(None, word1, word2).ratio()

    def finalize_execution(self) -> None:
        """Finalize the execution of the bot.

        Performs steps to clean up and log the completion of the bot's execution.
        """
        window_handles = self.driver.window_handles
        self.row += 1
        if window_handles:
            self.driver.delete_all_cookies()
            self.driver.quit()

        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        minutes, seconds = divmod(int(execution_time), 60)

        self.end_prt("Finalizado")

        self.type_log = "success"
        self.message = f"Fim da execução, tempo: {minutes} minutos e {seconds} segundos"
        self.prt()

    def install_cert(self) -> None:
        """Install a certificate if it is not already installed.

        Checks for the presence of a certificate and installs it using certutil if absent.
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
                resultado = subprocess.run(  # nosec: B603 # noqa: S603
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

    def group_date_all(self, data: dict[str, dict[str, str]]) -> list[dict[str, str]]:
        """Group date and vara information from the input data into a list of records.

        Args:
            data (dict[str, dict[str, str]]): A dictionary where the keys are 'vara'
                and the values are dictionaries with dates as keys and entries as values.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing grouped data.

        """
        records = []
        for vara, dates in data.items():
            for date, entries in dates.items():
                for entry in entries:
                    record = {"Data": date, "Vara": vara}
                    record.update(entry)
                    records.append(record)
        return records

    def group_keys(self, data: list[dict[str, str]]) -> dict[str, dict[str, str]]:
        """Group keys from a list of dictionaries.

        Args:
            data (list[dict[str, str]]): A list of dictionaries with string keys and values.

        Returns:
            dict[str, dict[str, str]]: A dictionary grouping keys with their corresponding values.

        """
        record = {}
        for pos, entry in enumerate(data):
            for key, value in entry.items():
                if key not in record:
                    record[key] = {}
                record[key][str(pos)] = value
        return record

    def gpt_chat(self, text_mov: str) -> str:
        """Analyzes a legal document text and adjusts the response based on the document type.

        Uses the OpenAI GPT model to analyze the provided text and generate a response
        identifying the document type and extracting relevant information.

        Args:
            text_mov (str): The text of the legal document to be analyzed.

        Returns:
            str: The adjusted response based on the document type.

        Raises:
            Exception: If an error occurs during the API call or processing.

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
        """Check if the given text is in a date-like format.

        Args:
            text (str): The text to be checked.

        Returns:
            bool: True if the text matches a date-like pattern, False otherwise.

        """
        date_like_pattern = r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"
        return bool(re.search(date_like_pattern, text))
