import os
import re
import ssl
import subprocess
import time
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List

import pandas as pd
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from pandas import Timestamp
from werkzeug.utils import secure_filename

from ..common import ErroDeExecucao
from ..shared import PropertiesCrawJUD
from .auth import AuthBot
from .Driver import DriverBot
from .elements import ElementsBot
from .interator import Interact
from .MakeTemplate import MakeXlsx
from .PrintLogs import printbot
from .search import SearchBot

__all__ = [
    AuthBot,
    MakeXlsx,
    ElementsBot,
    Interact,
    DriverBot,
    SearchBot,
    printbot,
]


class OtherUtils(PropertiesCrawJUD):

    prt = printbot.print_msg
    end_prt = printbot.end_bot

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

    @property
    def elaw_data(self) -> Dict[str, str]:
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
    def cities_Amazonas(self) -> dict[str, str]:
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

    @classmethod
    def dataFrame(cls) -> list[dict[str, str]]:
        """
        Converts an Excel file to a list of dictionaries with formatted data.
        This method reads an Excel file specified by the instance's path arguments,
        processes the data by formatting dates and floats, and returns the data as
        a list of dictionaries.
        Returns:
            list[dict[str, str]]: A list of dictionaries where each dictionary
            represents a row in the Excel file with formatted data.
        Raises:
            FileNotFoundError: If the specified Excel file does not exist.
            ValueError: If there is an issue reading the Excel file.
        """

        input_file = Path(cls.path_args).joinpath(cls.xlsx).resolve()

        df = pd.read_excel(input_file)
        df.columns = df.columns.str.upper()

        for col in df.columns.to_list():
            df[col] = df[col].apply(
                lambda x: (
                    x.strftime("%d/%m/%Y")
                    if type(x) is datetime or type(x) is Timestamp
                    else x
                )
            )

        for col in df.select_dtypes(include=["float"]).columns.to_list():
            df[col] = df[col].apply(lambda x: "{:.2f}".format(x).replace(".", ","))

        vars_df = []

        df_dicted = df.to_dict(orient="records")
        for item in df_dicted:
            for key, value in item.items():
                if str(value) == "nan":
                    item.update({key: None})

            vars_df.append(item)

        return vars_df

    @classmethod
    def elawFormats(cls, data: dict[str, str]) -> dict[str, str]:
        """
        Formats the given data dictionary according to specific rules.
        Args:
            data (dict[str, str]): A dictionary containing key-value pairs to be formatted.
        Returns:
            dict[str, str]: The formatted dictionary.
        Rules:
            - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
            - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
            - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
            - If the value is an integer or float, format it to two decimal places and replace the decimal point with a comma.
            - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".
        """

        data_listed = list(data.items())
        for key, value in data_listed:

            if not value.strip():
                data.pop(key)

            if key.upper() == "TIPO_EMPRESA":
                data.update({"TIPO_PARTE_CONTRARIA": "Autor"})
                if value.upper() == "RÉU":
                    data.update({"TIPO_PARTE_CONTRARIA": "Autor"})

            elif key.upper() == "COMARCA":
                set_locale = cls.cities_Amazonas().get(value, None)
                if not set_locale:
                    set_locale = "Outro Estado"

                data.update({"CAPITAL_INTERIOR": set_locale})

            elif key == "DATA_LIMITE" and not data.get("DATA_INICIO"):
                data.update({"DATA_INICIO": value})

            elif type(value) is int or type(value) is float:
                data.update({key: "{:.2f}".format(value).replace(".", ",")})

            elif key == "CNPJ_FAVORECIDO" and not value:
                data.update({key: "04.812.509/0001-90"})

        return data

    @classmethod
    def calc_time(cls) -> list:
        """
        Calculate the elapsed time since the start time and return it as a list of minutes and seconds.
        Returns:
            list: A list containing two integers:
                - minutes (int): The number of minutes of the elapsed time.
                - seconds (int): The number of seconds of the elapsed time.
        """

        end_time = time.perf_counter()
        execution_time = end_time - cls.start_time
        calc = execution_time / 60
        splitcalc = str(calc).split(".")
        minutes = int(splitcalc[0])
        seconds = int(float(f"0.{splitcalc[1]}") * 60)

        return [minutes, seconds]

    @classmethod
    def append_moves(cls) -> None:
        """
        Appends movements to the spreadsheet if there are any movements to append.
        This method checks if there are any movements stored in the `cls.appends` list.
        If there are, it iterates over each movement and calls the `cls.append_success`
        method to save the movement to the spreadsheet with a success message.
        Raises:
            ErroDeExecucao: If no movements are found in the `cls.appends` list.
        """

        if len(cls.appends) > 0:

            for append in cls.appends:

                cls.append_success(
                    append, "Movimentação salva na planilha com sucesso!!"
                )

        elif len(cls.appends) == 0:
            raise ErroDeExecucao("Nenhuma Movimentação encontrada")

    @classmethod
    def append_success(cls, data, message: str = None, fileN: str = None) -> None:

        if not message:
            message = "Execução do processo efetuada com sucesso!"

        def save_info(data: list[dict[str, str]]):

            output_success = cls.path

            chk_not_path = output_success is None

            if fileN is not None or chk_not_path:
                output_success = Path(cls.path).parent.resolve().joinpath(fileN)

            if not output_success.exists():
                df = pd.DataFrame(data)
                df = df.to_dict(orient="records")

            elif output_success.exists():

                df = pd.read_excel(output_success)
                df = df.to_dict(orient="records")
                df.extend(data)

            new_data = pd.DataFrame(df)
            new_data.to_excel(output_success, index=False)

        typeD = type(data) is list and all(isinstance(item, dict) for item in data)

        if not typeD:

            data2 = {}

            for item in cls().nomes_colunas:
                data2.update({item: ""})

            for item in data:
                for key, value in list(data2.items()):
                    if not value:
                        data2.update({key: item})
                        break

            data.clear()
            data.append(data2)

        save_info(data)

        if message:
            if cls.type_log == "log":
                cls.type_log = "success"

            cls.message = message
            cls.prt()

    @classmethod
    def count_doc(cls, doc: str) -> str | None:

        tipo_doc = None
        numero = "".join(filter(str.isdigit, doc))

        if len(numero) == 11:
            tipo_doc = "cpf"

        elif len(numero) == 14:
            tipo_doc = "cnpj"

        return tipo_doc

    @classmethod
    def append_validarcampos(cls, data: List[Dict[str, str]]) -> None:

        nomeplanilha = f"CAMPOS VALIDADOS PID {cls.pid}.xlsx"
        planilha_validar = Path(cls.path).parent.resolve().joinpath(nomeplanilha)
        if not os.path.exists(planilha_validar):
            df = pd.DataFrame(data)
            df = df.to_dict(orient="records")

        elif os.path.exists(planilha_validar):
            df = pd.read_excel(planilha_validar)
            df = df.to_dict(orient="records")
            df.extend(data)

        new_data = pd.DataFrame(df)
        new_data.to_excel(planilha_validar, index=False)

    @classmethod
    def append_error(cls, data: dict[str, str] = None) -> None:

        if not os.path.exists(cls.path_erro):
            df = pd.DataFrame(data)
            df = df.to_dict(orient="records")

        elif os.path.exists(cls.path_erro):
            df = pd.read_excel(cls.path_erro)
            df = df.to_dict(orient="records")
            df.extend([data])

        new_data = pd.DataFrame(df)
        new_data.to_excel(cls.path_erro, index=False)

    @classmethod
    def get_recent(cls, folder: str) -> str | None:
        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        files = [f for f in files if os.path.isfile(f)]
        files = list(
            filter(
                lambda x: ".pdf" in x.lower() and ".crdownload" not in x.lower(),
                files,
            )
        )
        files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        return files[0] if files else None

    @classmethod
    def format_String(cls, string: str) -> str:

        return secure_filename(
            "".join(
                [
                    c
                    for c in unicodedata.normalize("NFKD", string)
                    if not unicodedata.combining(c)
                ]
            )
        )

    @classmethod
    def normalizar_nome(cls, word: str):
        """

        ### (function) def normalizar_nome(cls, word: str) -> str

        Função para normalizar os nomes (removendo caracteres especiais)
        Remove espaços, substitui "_" e "-" por nada, e converte para minúsculas

        Args:
            word (str): palavra a ser 'normalizada'

        Returns:
            str: nome normalizado
        """
        #
        return re.sub(r"[\s_\-]", "", word).lower()

    @classmethod
    def similaridade(cls, word1: str, word2: str) -> float:
        """
        ### similaridade

        Função para comparar similaridade


        Args:
            word1 (str): Palavra 1
            word2 (str): Palavra 2

        Returns:
            float: porcentagem de similaridade
        """
        return SequenceMatcher(None, word1, word2).ratio()

    @classmethod
    def finalize_execution(cls) -> None:

        window_handles = cls.driver.window_handles
        cls.row = cls.row + 1
        if len(window_handles) > 0:

            cls.driver.delete_all_cookies()
            cls.driver.quit()

        end_time = time.perf_counter()
        execution_time = end_time - cls.start_time
        calc = execution_time / 60
        minutes = int(calc)
        seconds = int((calc - minutes) * 60)

        cls.end_prt("Finalizado")

        cls.type_log = "success"
        cls.message = f"Fim da execução, tempo: {minutes} minutos e {seconds} segundos"
        cls.prt()

    @classmethod
    def install_cert(cls) -> None:

        installed = cls.CertIsInstall(cls.name_cert.split(".pfx")[0])

        if installed is False:

            path_cert = str(os.path.join(cls.output_dir_path, cls.name_cert))
            comando = [
                "certutil",
                "-importpfx",
                "-user",
                "-f",
                "-p",
                cls.token,
                "-silent",
                path_cert,
            ]
            try:
                # Quando você passa uma lista, você geralmente não deve usar shell=True
                resultado = subprocess.run(
                    comando,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                cls.message = str(resultado.stdout)
                cls.type_log = str("log")
                cls.prt()

            except subprocess.CalledProcessError as e:
                raise e

    @classmethod
    def CertIsInstall(cls, crt_sbj_nm: str, store: str = "MY") -> bool:
        """
        Verifica se um certificado PFX específico está instalado no repositório 'MY'.

        Arguments:
            crt_sbj_nm (str): Nome do Assunto (Subject) do certificado para buscar.
            param store (str): Nome do repositório de certificados a ser verificado (default: "MY").

        :return: True se o certificado for encontrado, False caso contrário.
        """
        for cert, encoding, trust in ssl.enum_certificates(store):
            try:
                # Converte o certificado em formato DER para objeto X509
                x509_cert = x509.load_der_x509_certificate(cert, default_backend())

                # Obtém o nome do Assunto (Subject)
                subject_name = x509_cert.subject.rfc4514_string()

                # Verifica se o nome fornecido corresponde ao do certificado
                if crt_sbj_nm in subject_name:
                    return True
            except Exception as e:
                print(f"Erro ao processar o certificado: {e}")

        return False

    @classmethod
    def group_date_all(cls, data: dict[str, dict[str, str]]) -> list[dict[str, str]]:

        records = []
        for vara, dates in data.items():
            record = {}
            for date, entries in dates.items():
                for entry in entries:

                    record.update({"Data": date, "Vara": vara})
                    record.update(entry)
                    records.append(record)

        return records

    @classmethod
    def group_keys(cls, data: list[dict[str, str]]) -> dict[str, str]:

        record = {}
        for pos, entry in enumerate(data):
            for key, value in entry.items():

                if not record.get(key):
                    record.update({key: {}})

                record.get(key).update({str(pos): value})
        return record

    @classmethod
    def gpt_chat(cls, text_mov: str) -> str:

        try:

            time.sleep(5)
            client = cls.OpenAI_client
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um assistente jurídico especializado em analisar processos judiciais. "
                            "Seu objetivo é identificar o tipo de documento (como petição inicial, contestação, "
                            "sentença, decisão interlocutória, etc.) e ajustar sua resposta com base no tipo do documento:"
                            "\n- Para sentenças e acórdãos: Extraia exclusivamente os valores mencionados no dispositivo "
                            "ou no conteúdo relacionado a condenações, como danos morais e materiais. Retorne apenas o valor e "
                            "o tipo do valor de forma resumida, no formato: 'Danos morais: R$ XXXX,XX; Danos materiais: R$ XXXX,XX; Inexigibilidade de débito: R$ XXXX,XX'."
                            "Nas Sentenças e acordãos, procure fazer diferenciação dos valores para evitar erros como entregar valores de limite de multa como danos morais ou qualquer "
                            "\n outro de forma errônea."
                            "\n- Para petições iniciais: Forneça um resumo do tema principal do processo com base na petição inicial e, em seguida, extraia os valores e os tipos de indenização solicitados pelo autor, como danos morais, materiais, lucros cessantes, inexigibilidade, ou outros pedidos monetários. "
                            "Resuma no formato: 'Tipo de documento: Petição Inicial; Assunto: [Resumo do tema do processo]; Danos morais: R$ XXXX,XX; Danos materiais: R$ XXXX,XX; Lucros cessantes: R$ XXXX,XX; Inexigibilidade: R$ XXXX,XX'."
                            "Caso não haja valores específicos, forneça apenas o resumo do tema principal do processo."
                            "\n- Para contestações: Forneça um resumo objetivo da linha de defesa apresentada."
                            "\n- Para decisões interlocutórias: Identifique claramente o tipo de decisão e extraia, de forma minimalista, "
                            "as obrigações ou designações impostas, como deferimento ou indeferimento de pedidos, determinações processuais, "
                            "ou outras medidas relevantes. Resuma no formato: 'Tipo de documento: Decisão interlocutória; Assunto: [Obrigações/designações principais]'."
                            "\n- Identifique claramente o tipo de documento no início da resposta."
                            "- Exemplo de comportamento esperado:\n"
                            "  - Entrada: 'Sentença: Condenou o réu a pagar R$ 10.000,00 de danos morais e R$ 5.000,00 de danos materiais.'\n"
                            "  - Saída: 'Danos morais: R$ 10.000,00; Danos materiais: R$ 5.000,00'\n"
                            "  - Entrada: 'Petição Inicial: O autor requer indenização por danos morais de R$ 50.000,00, danos materiais de R$ 30.000,00, e lucros cessantes de R$ 20.000,00, decorrentes de um acidente de trânsito.'\n"
                            "  - Saída: 'Tipo de documento: Petição Inicial; Assunto: Pedido de indenização por acidente de trânsito; Danos morais: R$ 50.000,00; Danos materiais: R$ 30.000,00; Lucros cessantes: R$ 20.000,00.'\n"
                            "  - Entrada: 'Petição Inicial: O autor solicita a declaração de inexigibilidade de débito no valor de R$ 15.000,00.'\n"
                            "  - Saída: 'Tipo de documento: Petição Inicial; Assunto: Pedido de declaração de inexigibilidade de débito; Inexigibilidade de débito: R$ 15.000,00.'\n"
                            "  - Entrada: 'Petição Inicial: O autor pleiteia indenização por danos morais e materiais decorrentes de erro médico.'\n"
                            "  - Saída: 'Tipo de documento: Petição Inicial; Assunto: Pedido de indenização por erro médico; Danos morais: Não especificado; Danos materiais: Não especificado.'\n"
                            "  - Entrada: 'Decisão interlocutória: O pedido de tutela foi deferido para reintegração de posse do imóvel.'\n"
                            "  - Saída: 'Tipo de documento: Decisão interlocutória; Assunto: Pedido de tutela deferido para reintegração de posse.'"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Analise o seguinte texto e ajuste sua resposta de acordo com o tipo de documento: {text_mov}."
                        ),
                    },
                ],
                temperature=0.1,
                max_tokens=300,  # Ajuste conforme necessário
            )

            choices = completion.choices
            choice = choices[0]
            choice_message = choice.message
            text = choice_message.content

            if not text:
                text = text_mov

            return text
        except Exception as e:
            print(e)
            raise e

    @classmethod
    def text_is_a_date(cls, text: str) -> bool:

        # Regex para verificar se o texto pode ser uma data (opcional)
        date_like_pattern = (
            r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"  # Exemplo: 2023-01-08 ou 08/01/2023
        )
        if re.search(date_like_pattern, text):
            return True
        else:
            return False
