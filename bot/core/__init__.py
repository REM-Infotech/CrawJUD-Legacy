"""
Core module for the CrawJUD bot.

This module provides the main functionalities and configurations
for the CrawJUD bot, including setup and authentication processes.
"""

from __future__ import annotations

import json
import logging
import platform
import traceback

from .. import (
    BarColumn,
    DownloadColumn,
    Group,
    Live,
    Panel,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    pd,
)

if platform.system() == "Windows":
    from .. import Application

from datetime import datetime
from pathlib import Path

from pytz import timezone

from ..common import ErroDeExecucao
from ..shared import PropertiesCrawJUD, TypeHint

__all__ = [
    pd,
    "Application",
    Group,
    Live,
    Panel,
    Progress,
    TaskID,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
]


class CrawJUD(PropertiesCrawJUD):
    """
    CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    def prt(self) -> None:
        """
        Print a message using the PrintBot's print_msg method.

        This method invokes the print_msg method of the PrintBot instance
        to display messages.
        """
        self.PrintBot.print_msg()

    def end_prt(self, status: str) -> None:
        """
        End the print session with the given status.

        Args:
            status (str): The status message to indicate the end of the print session.

        """
        self.PrintBot.end_prt(status)

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the CrawJUD instance with provided arguments.

        Loads configurations, sets up paths, and initializes the driver.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        self.kwrgs = kwargs
        list_kwargs = list(kwargs.items())
        for key, value in list_kwargs:
            if key == "path_args":
                value = Path(value).resolve()

            setattr(self, key, value)

        with open(self.path_args, "rb") as f:
            json_f: dict[str, str | int] = json.load(f)

            self.kwrgs = json_f

            for key, value in json_f.items():
                setattr(self, key, value)

        self.state_or_client = self.state if self.state is not None else self.client

    def __getattr__(self, nome: str) -> TypeHint:
        """
        Retrieve an attribute dynamically.

        Attempts to get the attribute 'nome' from the keyword arguments.
        If not found, it searches in the CrawJUD class dictionary and
        then in the PropertiesCrawJUD class dictionaries.

        Args:
            nome (str): The name of the attribute to retrieve.

        Returns:
            TypeHint: The value of the requested attribute.

        Raises:
            AttributeError: If the attribute is not found in any sources.

        """
        item = self.kwrgs.get(nome, None)

        if not item:
            item = CrawJUD.__dict__.get(nome, None)

            if not item:
                item = PropertiesCrawJUD.kwrgs_.get(nome, None)

        return item

    # def set_permissions_recursive(self, path: Path, permissions: int) -> None:
    #     # Converte o caminho para um objeto Path, caso ainda não seja
    #     path = Path(path)

    #     # Define a permissão para o próprio diretório
    #     path.chmod(permissions)

    #     # Itera sobre todos os arquivos e diretórios dentro da pasta
    #     for item in path.rglob("*"):  # rglob percorre recursivamente

    #         try:
    #             item.chmod(permissions)

    #         except FileNotFoundError:
    #             continue

    def setup(self) -> None:
        """
        Set up the bot by loading configuration and preparing the environment.

        Performs the following steps:
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
            Exception: If any error occurs during the setup process.

        """
        self.row = 0

        try:
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

            self.path = Path(self.output_dir_path).joinpath(f"Sucessos - PID {self.pid} {time_xlsx}.xlsx").resolve()

            self.path_erro = Path(self.output_dir_path).joinpath(f"Erros - PID {self.pid} {time_xlsx}.xlsx").resolve()

            self.name_colunas = self.MakeXlsx.make_output("sucesso", self.path)
            self.MakeXlsx.make_output("erro", self.path_erro)

            if not self.xlsx:
                self.data_inicio = datetime.strptime(self.data_inicio, "%Y-%m-%d")
                self.data_fim = datetime.strptime(self.data_fim, "%Y-%m-%d")

            driver, wait = self.DriverLaunch()

            self.driver = driver
            self.wait = wait

            # self.set_permissions_recursive(Path(self.output_dir_path).parent.resolve())

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
        """
        Authenticate the bot using the specified login method.

        Checks if the bot is logged in using the provided authentication method.
        Logs a success message if login is successful.
        Quits the driver, logs an error message, and raises an exception if login fails.

        Raises:
            ErroDeExecucao: If the login fails.
            Exception: For any other errors during authentication.

        """
        try:
            if self.login_method:
                chk_logged = self.AuthBot()
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
            err = traceback.format_exc()
            logging.exception(err)
            self.row = 0
            self.message = "Erro ao realizar login"
            self.type_log = "error"

            self.prt()
            self.end_prt("Falha ao iniciar")
            if self.driver:
                self.driver.quit()

            raise e
