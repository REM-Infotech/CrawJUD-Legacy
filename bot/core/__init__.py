import json
import os
import platform
import re
import shutil
import ssl
import subprocess
import time
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytz
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# from openai._streaming import Stream
# from openai.types.chat.chat_completion import ChatCompletion
# from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

# from tenacity import (  # for exponential backoff
#     retry,
#     stop_after_attempt,
#     wait_random_exponential,
# )
from werkzeug.utils import secure_filename

from ..shared import PropertiesCrawJUD
from ..Utils import OtherUtils, SetupDriver, printbot

# from memory_profiler import profile

# from openai import OpenAI


# fp = open("crawjud_profiler.log", "w+")


class CrawJUD(PropertiesCrawJUD):

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    @classmethod
    def set_permissions_recursive(path: Path, permissions: int = 0o775):
        # Converte o caminho para um objeto Path, caso ainda não seja
        path = Path(path)

        # Define a permissão para o próprio diretório
        path.chmod(permissions)

        # Itera sobre todos os arquivos e diretórios dentro da pasta
        for item in path.rglob("*"):  # rglob percorre recursivamente
            item.chmod(permissions)

    @classmethod
    def setup(cls) -> None:
        """
        Sets up the bot by loading configuration from a JSON file, initializing various attributes,
        and preparing the environment for the bot to run.
        This method performs the following steps:
        1. Loads configuration from a JSON file specified by `cls.path_args`.
        2. Sets attributes based on the loaded configuration.
        3. Initializes logging and output directory paths.
        4. Prepares a list of arguments for the system.
        5. Installs certificates if `cls.name_cert` is specified.
        6. Creates Excel files for logging successes and errors.
        7. Parses date strings into datetime objects if `cls.xlsx` is not specified.
        8. Sets the state or client attribute.
        9. Launches the driver.
        Raises:
            Exception: If any error occurs during the setup process, it logs the error and raises the exception.
        """

        try:
            with open(cls.path_args, "rb") as f:
                json_f: dict[str, str | int] = json.load(f)

                cls.kwrgs = json_f

                for key, value in json_f.items():
                    setattr(cls, key, value)

            cls.message = str("Inicializando robô")
            cls.type_log = str("log")
            cls.prt()

            cls.output_dir_path = Path(cls.path_args).parent.resolve().__str__()
            # time.sleep(10)
            cls.list_args = [
                "--ignore-ssl-errors=yes",
                "--ignore-certificate-errors",
                "--display=:99",
                "--window-size=1600,900",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--kiosk-printing",
            ]
            cls.system
            if cls.name_cert:

                cls.install_cert()

            time_xlsx = datetime.now(pytz.timezone("America/Manaus")).strftime(
                "%d-%m-%y"
            )

            namefile = f"Sucessos - PID {cls.pid} {time_xlsx}.xlsx"
            cls.path = f"{cls.output_dir_path}/{namefile}"

            namefile_erro = f"Erros - PID {cls.pid} {time_xlsx}.xlsx"
            cls.path_erro = f"{cls.output_dir_path}/{namefile_erro}"

            cls.name_colunas = cls.MakeXlsx("sucesso", cls.typebot).make_output(
                cls.path
            )
            cls.MakeXlsx("erro", cls.typebot).make_output(cls.path_erro)

            if not cls.xlsx:

                cls.data_inicio = datetime.strptime(cls.data_inicio, "%Y-%m-%d")
                cls.data_fim = datetime.strptime(cls.data_fim, "%Y-%m-%d")

            cls.state_or_client = cls.state if cls.state is not None else cls.client
            cls.DriverLaunch()

            cls.set_permissions_recursive(Path(cls.output_dir_path).parent.resolve())

        except Exception as e:

            cls.row = 0
            cls.message = "Falha ao iniciar"
            cls.type_log = "error"
            cls.prt()
            cls.end_prt("Falha ao iniciar")

            if cls.driver:
                cls.driver.quit()

            raise e

    # @profile(stream=fp)
    @classmethod
    def auth_bot(cls) -> None:

        from ..Utils import AuthBot

        try:
            """
            Authenticates the bot using the specified login method.
            This method checks if the bot is logged in using the provided authentication method.
            If the login is successful, it logs a success message.
            If the login fails, it quits the driver, logs an error message, and raises an exception.
            Returns:
                None
            Raises:
                Exception: If the login fails.
            """

            if cls.login_method:
                chk_logged = AuthBot.auth()
                if chk_logged is True:

                    cls.message = "Login efetuado com sucesso!"
                    cls.type_log = "log"
                    cls.prt()

                elif chk_logged is False:

                    cls.driver.quit()
                    cls.message = "Erro ao realizar login"
                    cls.type_log = "error"
                    cls.prt()
                    raise Exception(message=cls.message)

        except Exception as e:

            print(e)
            cls.row = 0
            cls.message = "Erro ao realizar login"
            cls.type_log = "error"

            cls.prt()
            cls.end_prt("Falha ao iniciar")
            if cls.driver:
                cls.driver.quit()

            raise e

    # @profile(stream=fp)
    @classmethod
    def end_prt(cls, status: str) -> None:

        print_bot = cls.printtext()
        print_bot.end_bot(status)

    @classmethod
    def prt(cls) -> None:

        graphic = cls.graphicMode_
        cls.graphicMode = graphic
        printbot.print_msg()
        # thread_printbot = threading.Thread(
        #     target=print_bot, name="printbot {}".format(cls.pid)
        # )
        # thread_printbot.start()

    def Select2_ELAW(self, elementSelect: str, to_Search: str) -> None:
        OtherUtils.select2elaw(elementSelect, to_Search)

    # @profile(stream=fp)

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

    def append_error(cls, data: dict[str, str] = None):

        if not os.path.exists(cls.path_erro):
            df = pd.DataFrame(data)
            df = df.to_dict(orient="records")

        elif os.path.exists(cls.path_erro):
            df = pd.read_excel(cls.path_erro)
            df = df.to_dict(orient="records")
            df.extend([data])

        new_data = pd.DataFrame(df)
        new_data.to_excel(cls.path_erro, index=False)

    # @profile(stream=fp)
    def get_recent(cls, folder: str):
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

    # @profile(stream=fp)
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

    # @profile(stream=fp)
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

    # @profile(stream=fp)
    def similaridade(cls, word1: str, word2: str):
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

    # @profile(stream=fp)
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
    def DriverLaunch(cls, message: str = "Inicializando WebDriver") -> WebDriver:

        try:
            cls.message = message
            cls.type_log = "log"
            cls.prt()

            list_args = cls.list_args

            chrome_options = Options()
            cls.chr_dir = str(
                os.path.join(Path(__file__).cwd(), "exec", cls.pid, "chrome")
            )

            user = os.environ.get(
                "USER", os.environ.get("LOGNAME", os.environ.get("USERNAME", "root"))
            )
            if user != "root" or platform.system() != "Linux":
                list_args.remove("--no-sandbox")

            if platform.system() == "Windows" and cls.login_method == "cert":
                state = str(cls.state)
                cls.path_accepted = str(
                    os.path.join(
                        Path(__file__).cwd(),
                        "Browser",
                        state,
                        cls.username,
                        "chrome",
                    )
                )
                path_exist = os.path.exists(cls.path_accepted)
                if path_exist:

                    for root, dirs, files in os.walk(cls.path_accepted):
                        try:
                            shutil.copytree(root, cls.chr_dir)
                        except Exception as e:
                            print(e)

                elif not path_exist:
                    os.makedirs(cls.path_accepted, exist_ok=True, mode=0o775)

            chrome_options.add_argument(f"user-data-dir={cls.chr_dir}")
            for argument in list_args:
                chrome_options.add_argument(argument)

            this_path = Path(__file__).parent.resolve().__str__()
            path_extensions = os.path.join(this_path, "extensions")
            for root, dirs, files in os.walk(path_extensions):
                for file_ in files:
                    if ".crx" in file_:
                        path_plugin = os.path.join(root, file_)
                        chrome_options.add_extension(path_plugin)

            chrome_prefs = {
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0,
                "printing.print_preview_sticky_settings.appState": json.dumps(
                    cls.settings
                ),
                "download.default_directory": "{}".format(
                    os.path.join(cls.output_dir_path)
                ),
            }

            path_chrome = None
            chrome_options.add_experimental_option("prefs", chrome_prefs)
            pid_path = Path(cls.path_args).parent.resolve()
            getdriver = SetupDriver(destination=pid_path)

            abs_pidpath = Path(pid_path).absolute()

            if message != "Inicializando WebDriver":

                version = getdriver.code_ver
                chrome_name = f"chromedriver{version}"
                if platform.system() == "Windows":
                    chrome_name += ".exe"

                if Path(os.path.join(abs_pidpath, chrome_name)).exists():
                    path_chrome = Path(pid_path).parent.resolve().joinpath(chrome_name)

            if path_chrome is None:
                path_chrome = Path(pid_path).parent.resolve().joinpath(getdriver())

            path_chrome.chmod(0o777, follow_symlinks=True)

            driver = webdriver.Chrome(
                service=Service(path_chrome), options=chrome_options
            )

            # driver.maximize_window()

            wait = WebDriverWait(driver, 20, 0.01)
            driver.delete_all_cookies()

            cls.driver = driver
            cls.wait = wait

            cls.message = "WebDriver inicializado"
            cls.type_log = "log"
            cls.prt()

            return driver

        except Exception as e:
            raise e

    @classmethod
    def install_cert(cls) -> None:

        installed = cls.is_pfx_certificate_installed(cls.name_cert.split(".pfx")[0])

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

    # @profile(stream=fp)
    @classmethod
    def is_pfx_certificate_installed(
        cls, cert_subject_name: str, store_name: str = "MY"
    ) -> bool:
        """
        Verifica se um certificado PFX específico está instalado no repositório 'MY'.

        Arguments:
            cert_subject_name (str): Nome do Assunto (Subject) do certificado para buscar.
            param store_name (str): Nome do repositório de certificados a ser verificado (default: "MY").

        :return: True se o certificado for encontrado, False caso contrário.
        """
        for cert, encoding, trust in ssl.enum_certificates(store_name):
            try:
                # Converte o certificado em formato DER para objeto X509
                x509_cert = x509.load_der_x509_certificate(cert, default_backend())

                # Obtém o nome do Assunto (Subject)
                subject_name = x509_cert.subject.rfc4514_string()

                # Verifica se o nome fornecido corresponde ao do certificado
                if cert_subject_name in subject_name:
                    return True
            except Exception as e:
                print(f"Erro ao processar o certificado: {e}")

        return False

    # @profile(stream=fp)
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

    # @profile(stream=fp)
    def group_keys(cls, data: list[dict[str, str]]) -> dict[str, str]:

        record = {}
        for pos, entry in enumerate(data):
            for key, value in entry.items():

                if not record.get(key):
                    record.update({key: {}})

                record.get(key).update({str(pos): value})
        return record

    # @profile(stream=fp)

    # @profile(stream=fp)
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

    # @profile(stream=fp)
    def text_is_a_date(cls, text: str) -> bool:

        # Regex para verificar se o texto pode ser uma data (opcional)
        date_like_pattern = (
            r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"  # Exemplo: 2023-01-08 ou 08/01/2023
        )
        if re.search(date_like_pattern, text):
            return True
        else:
            return False
