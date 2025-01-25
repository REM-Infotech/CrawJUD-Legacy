import json
from datetime import datetime
from pathlib import Path

from pytz import timezone
from ..emulate import Emulate
from ..common import ErroDeExecucao


class CrawJUD(Emulate):

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    def prt(self) -> None:
        """Print message"""

        self.printtext.print_msg()

    def end_prt(self, status: str) -> None:

        self.printtext.end_prt(status)

    def __init__(self, *args, **kwargs) -> None:

        self.kwrgs = kwargs
        list_kwargs = list(kwargs.items())
        for key, value in list_kwargs:

            if key == "path_args":
                value = Path(value).resolve()

            setattr(self, key, value)

    def set_permissions_recursive(self, path: Path, permissions: int = 0o775) -> None:
        # Converte o caminho para um objeto Path, caso ainda não seja
        path = Path(path)

        # Define a permissão para o próprio diretório
        path.chmod(permissions)

        # Itera sobre todos os arquivos e diretórios dentro da pasta
        for item in path.rglob("*"):  # rglob percorre recursivamente
            item.chmod(permissions)

    def setup(self) -> None:
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
        self.row = 0

        try:
            with open(self.path_args, "rb") as f:
                json_f: dict[str, str | int] = json.load(f)

                self.kwrgs = json_f

                for key, value in json_f.items():
                    setattr(self, key, value)

            self.message = str("Inicializando robô")
            self.type_log = str("log")
            self.prt()

            self.output_dir_path = Path(self.path_args).parent.resolve()
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
            if self.name_cert:

                self.install_cert()

            time_xlsx = datetime.now(timezone("America/Manaus")).strftime("%d-%m-%y")

            self.path = (
                Path(self.output_dir_path)
                .joinpath(f"Sucessos - PID {self.pid} {time_xlsx}.xlsx")
                .resolve()
            )

            self.path_erro = (
                Path(self.output_dir_path)
                .joinpath(f"Erros - PID {self.pid} {time_xlsx}.xlsx")
                .resolve()
            )

            self.name_colunas = self.MakeXlsx.make_output("sucesso", self.path)
            self.MakeXlsx.make_output("erro", self.path_erro)

            if not self.xlsx:

                self.data_inicio = datetime.strptime(self.data_inicio, "%Y-%m-%d")
                self.data_fim = datetime.strptime(self.data_fim, "%Y-%m-%d")

            self.state_or_client = self.state if self.state is not None else self.client
            driver, wait = self.DriverLaunch

            self.driver = driver
            self.wait = wait

            self.set_permissions_recursive(Path(self.output_dir_path).parent.resolve())

        except Exception as e:

            self.row = 0
            self.message = "Falha ao iniciar"
            self.type_log = "error"
            self.prt()
            self.end_prt("Falha ao iniciar")

            if self.driver:
                self.driver.quit()

            raise e

    def auth_bot(self) -> None:

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
                chk_logged = self.Auth_Bot()
                if chk_logged is True:

                    self.message = "Login efetuado com sucesso!"
                    self.type_log = "log"
                    self.prt()

                elif chk_logged is False:

                    self.driver.quit()
                    self.message = "Erro ao realizar login"
                    self.type_log = "error"
                    self.prt()
                    raise ErroDeExecucao(message=self.message)

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
