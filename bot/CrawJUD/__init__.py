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
from typing import Dict, List, Self, Union

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
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# from tenacity import (  # for exponential backoff
#     retry,
#     stop_after_attempt,
#     wait_random_exponential,
# )
from werkzeug.utils import secure_filename

from ..meta import PropertiesCrawJUD
from ..Utils.Driver import GetDriver

# from memory_profiler import profile

# from openai import OpenAI


TypeHint = Union[
    List[str],
    List[Dict[str, str | int | float | datetime]],
    Dict[str, str],
]

# fp = open("crawjud_profiler.log", "w+")


class CrawJUD(PropertiesCrawJUD):

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    def __init__(self, **kwargs) -> None:

        self.__dict__.update(kwargs)
        self.kwrgs = kwargs

    def __getattr__(self, nome: str) -> TypeHint:

        item = self.kwrgs.get(nome, None)

        if not item:
            item = CrawJUD.__dict__.get(nome, None)

            if not item:
                item = PropertiesCrawJUD.kwrgs_.get(nome, None)

        return item

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
    def setup(cls, self: Self) -> None:
        """
        Sets up the bot by loading configuration from a JSON file, initializing various attributes,
        and preparing the environment for the bot to run.
        This method performs the following steps:
        1. Loads configuration from a JSON file specified by `self.path_args`.
        2. Sets attributes based on the loaded configuration.
        3. Initializes logging and output directory paths.
        4. Prepares a list of arguments for the system.
        5. Installs certificates if `self.name_cert` is specified.
        6. Creates Excel files for logging successes and errors.
        7. Parses date strings into datetime objects if `self.xlsx` is not specified.
        8. Sets the state or client attribute.
        9. Launches the driver.
        Raises:
            Exception: If any error occurs during the setup process, it logs the error and raises the exception.
        """

        try:
            with open(self.path_args, "rb") as f:
                json_f: dict[str, str | int] = json.load(f)

                self.kwrgs = json_f

                for key, value in json_f.items():
                    setattr(self, key, value)

            self.message = str("Inicializando robô")
            self.type_log = str("log")
            self.prt()

            self.output_dir_path = Path(self.path_args).parent.resolve().__str__()
            # time.sleep(10)
            self.list_args = [
                "--ignore-ssl-errors=yes",
                "--ignore-certificate-errors",
                "--display=:99",
                "--window-size=1600,900",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--kiosk-printing",
            ]
            self.system
            if self.name_cert:

                self.install_cert()

            time_xlsx = datetime.now(pytz.timezone("America/Manaus")).strftime(
                "%d-%m-%y"
            )

            namefile = f"Sucessos - PID {self.pid} {time_xlsx}.xlsx"
            self.path = f"{self.output_dir_path}/{namefile}"

            namefile_erro = f"Erros - PID {self.pid} {time_xlsx}.xlsx"
            self.path_erro = f"{self.output_dir_path}/{namefile_erro}"

            self.name_colunas = self.MakeXlsx("sucesso", self.typebot).make_output(
                self.path
            )
            self.MakeXlsx("erro", self.typebot).make_output(self.path_erro)

            if not self.xlsx:

                self.data_inicio = datetime.strptime(self.data_inicio, "%Y-%m-%d")
                self.data_fim = datetime.strptime(self.data_fim, "%Y-%m-%d")

            self.state_or_client = self.state if self.state is not None else self.client
            self.DriverLaunch()

            cls.set_permissions_recursive(Path(self.output_dir_path).parent.resolve())

        except Exception as e:

            self.row = 0
            self.message = "Falha ao iniciar"
            self.type_log = "error"
            self.prt()
            self.end_prt("Falha ao iniciar")

            if self.driver:
                self.driver.quit()

            raise e

    # @profile(stream=fp)
    @classmethod
    def auth_bot(cls, self: Self) -> None:

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

            if self.login_method:
                chk_logged = AuthBot.auth()
                if chk_logged is True:

                    self.message = "Login efetuado com sucesso!"
                    self.type_log = "log"
                    self.prt()

                elif chk_logged is False:

                    self.driver.quit()
                    self.message = "Erro ao realizar login"
                    self.type_log = "error"
                    self.prt()
                    raise Exception(message=self.message)

        except Exception as e:

            print(e)
            self.row = 0
            self.message = "Erro ao realizar login"
            self.type_log = "error"

            self.prt()
            self.end_prt("Falha ao iniciar")
            if self.driver:
                self.driver.quit()

            raise e

    # @profile(stream=fp)
    def end_prt(self, status: str) -> None:

        print_bot = self.printtext()
        print_bot.end_bot(status)

    # @profile(stream=fp)
    def prt(self) -> None:

        self.printtext().print_msg()
        # thread_printbot = threading.Thread(
        #     target=print_bot, name="printbot {}".format(self.pid)
        # )
        # thread_printbot.start()

    # @profile(stream=fp)

    def append_validarcampos(self, data: List[Dict[str, str]]) -> None:

        nomeplanilha = f"CAMPOS VALIDADOS PID {self.pid}.xlsx"
        planilha_validar = Path(self.path).parent.resolve().joinpath(nomeplanilha)
        if not os.path.exists(planilha_validar):
            df = pd.DataFrame(data)
            df = df.to_dict(orient="records")

        elif os.path.exists(planilha_validar):
            df = pd.read_excel(planilha_validar)
            df = df.to_dict(orient="records")
            df.extend(data)

        new_data = pd.DataFrame(df)
        new_data.to_excel(planilha_validar, index=False)

    def append_error(self, data: dict[str, str] = None):

        if not os.path.exists(self.path_erro):
            df = pd.DataFrame(data)
            df = df.to_dict(orient="records")

        elif os.path.exists(self.path_erro):
            df = pd.read_excel(self.path_erro)
            df = df.to_dict(orient="records")
            df.extend([data])

        new_data = pd.DataFrame(df)
        new_data.to_excel(self.path_erro, index=False)

    # @profile(stream=fp)
    def get_recent(self, folder: str):
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
    def format_String(self, string: str) -> str:

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
    def normalizar_nome(self, word: str):
        """

        ### (function) def normalizar_nome(self, word: str) -> str

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
    def similaridade(self, word1: str, word2: str):
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
    def finalize_execution(self) -> None:

        window_handles = self.driver.window_handles
        self.row = self.row + 1
        if len(window_handles) > 0:

            self.driver.delete_all_cookies()
            self.driver.quit()

        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        calc = execution_time / 60
        minutes = int(calc)
        seconds = int((calc - minutes) * 60)

        self.end_prt("Finalizado")

        self.type_log = "success"
        self.message = f"Fim da execução, tempo: {minutes} minutos e {seconds} segundos"
        self.prt()

    # @profile(stream=fp)
    def DriverLaunch(self, message: str = "Inicializando WebDriver") -> WebDriver:

        try:
            self.message = message
            self.type_log = "log"
            self.prt()

            list_args = self.list_args

            chrome_options = Options()
            self.chr_dir = str(
                os.path.join(Path(__file__).cwd(), "exec", self.pid, "chrome")
            )

            user = os.environ.get(
                "USER", os.environ.get("LOGNAME", os.environ.get("USERNAME", "root"))
            )
            if user != "root" or platform.system() != "Linux":
                list_args.remove("--no-sandbox")

            if platform.system() == "Windows" and self.login_method == "cert":
                state = str(self.state)
                self.path_accepted = str(
                    os.path.join(
                        Path(__file__).cwd(),
                        "Browser",
                        state,
                        self.username,
                        "chrome",
                    )
                )
                path_exist = os.path.exists(self.path_accepted)
                if path_exist:

                    for root, dirs, files in os.walk(self.path_accepted):
                        try:
                            shutil.copytree(root, self.chr_dir)
                        except Exception as e:
                            print(e)

                elif not path_exist:
                    os.makedirs(self.path_accepted, exist_ok=True, mode=0o775)

            chrome_options.add_argument(f"user-data-dir={self.chr_dir}")
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
                    self.settings
                ),
                "download.default_directory": "{}".format(
                    os.path.join(self.output_dir_path)
                ),
            }

            path_chrome = None
            chrome_options.add_experimental_option("prefs", chrome_prefs)
            pid_path = Path(self.path_args).parent.resolve()
            getdriver = GetDriver(destination=pid_path)

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

            path_chrome.chmod(0o775)

            driver = webdriver.Chrome(
                service=Service(path_chrome), options=chrome_options
            )

            # driver.maximize_window()

            wait = WebDriverWait(driver, 20, 0.01)
            driver.delete_all_cookies()

            self.driver = driver
            self.wait = wait

            self.message = "WebDriver inicializado"
            self.type_log = "log"
            self.prt()

            return driver

        except Exception as e:
            raise e

    # @profile(stream=fp)
    def install_cert(self) -> None:

        installed = self.is_pfx_certificate_installed(self.name_cert.split(".pfx")[0])

        if installed is False:

            path_cert = str(os.path.join(self.output_dir_path, self.name_cert))
            comando = [
                "certutil",
                "-importpfx",
                "-user",
                "-f",
                "-p",
                self.token,
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

                self.message = str(resultado.stdout)
                self.type_log = str("log")
                self.prt()

            except subprocess.CalledProcessError as e:
                raise e

    # @profile(stream=fp)
    def is_pfx_certificate_installed(
        self, cert_subject_name: str, store_name: str = "MY"
    ):
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
    def group_date_all(self, data: dict[str, dict[str, str]]) -> list[dict[str, str]]:

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
    def group_keys(self, data: list[dict[str, str]]) -> dict[str, str]:

        record = {}
        for pos, entry in enumerate(data):
            for key, value in entry.items():

                if not record.get(key):
                    record.update({key: {}})

                record.get(key).update({str(pos): value})
        return record

    # @profile(stream=fp)
    def Select2_ELAW(self, elementSelect: str, to_Search: str) -> None:

        selector: WebElement = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elementSelect))
        )

        items = selector.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        elementsSelecting = elementSelect.replace("'", "'")
        if '"' in elementsSelecting:
            elementsSelecting = elementSelect.replace('"', "'")

        for item in items:

            value_item = item.get_attribute("value")
            cms = f"{elementsSelecting} > option[value='{value_item}']"
            text_item = self.driver.execute_script(f'return $("{cms}").text();')

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_Search.upper())

        if value_opt:

            command = f"$('{elementSelect}').val(['{value_opt}']);"
            command2 = f"$('{elementSelect}').trigger('change');"

            if "'" in elementSelect:
                command = f"$(\"{elementSelect}\").val(['{value_opt}']);"
                command2 = f"$(\"{elementSelect}\").trigger('change');"

            self.driver.execute_script(command)
            self.driver.execute_script(command2)

    # @profile(stream=fp)
    def gpt_chat(self, text_mov: str) -> str:

        try:

            time.sleep(5)
            client = self.OpenAI_client
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
    def text_is_a_date(self, text: str) -> bool:

        # Regex para verificar se o texto pode ser uma data (opcional)
        date_like_pattern = (
            r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}"  # Exemplo: 2023-01-08 ou 08/01/2023
        )
        if re.search(date_like_pattern, text):
            return True
        else:
            return False
