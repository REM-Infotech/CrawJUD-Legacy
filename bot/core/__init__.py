import json
from datetime import datetime
from pathlib import Path

from pytz import timezone

from ..shared import PropertiesCrawJUD
from ..Utils import (
    AuthBot,
    ElementsBot,
    Interact,
    MakeXlsx,
    OtherUtils,
    SearchBot,
    SetupDriver,
    count_doc,
    printbot,
)

__all__ = [
    ElementsBot,
    Interact,
    MakeXlsx,
    OtherUtils,
    SearchBot,
    SetupDriver,
    count_doc,
    printbot,
]


class CrawJUD(PropertiesCrawJUD):

    interact = Interact
    search_bot = SearchBot

    @property
    def isStoped(self) -> bool:

        file_check = Path(self.output_dir_path).resolve().joinpath(f"{self.pid}.flag")
        return file_check.exists()

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    @classmethod
    def set_permissions_recursive(path: Path, permissions: int = 0o775) -> None:
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

            time_xlsx = datetime.now(timezone("America/Manaus")).strftime("%d-%m-%y")

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

    @classmethod
    def auth_bot(cls) -> None:

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

    @classmethod
    def end_prt(cls, status: str) -> None:

        graphic = cls.graphicMode_
        cls.graphicMode = graphic
        printbot.end_bot(status)

    @classmethod
    def prt(cls) -> None:

        graphic = cls.graphicMode_
        cls.graphicMode = graphic
        printbot.print_msg()
