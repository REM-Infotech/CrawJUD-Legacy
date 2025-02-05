"""Module: core.

This module contains the CrawJUD class, which serves as the core framework for managing bot operations within the CrawJUD-Bots application.
"""  # noqa: E501

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

from ...shared import PropertiesCrawJUD, TypeHint
from ..common import ErroDeExecucao

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

logger = logging.getLogger(__name__)


class CrawJUD(PropertiesCrawJUD):
    """CrawJUD class.

    Serves as the core framework for managing bot operations, including setup, authentication, and attribute management.
    """

    settings = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    def prt(self) -> None:
        """Print a message using the PrintBot instance.

        This method delegates the printing of messages to the PrintBot's print_msg method.
        """
        self.PrintBot.print_msg()

    def end_prt(self, status: str) -> None:
        """End the print session with a given status.

        Args:
            status (str): The status message to log upon ending the print session.

        """
        self.PrintBot.end_prt(status)

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize a new CrawJUD instance.

        Sets up configurations, loads settings from a JSON file, and launches the web driver.

        Args:
            *args: Variable length argument list.
            **kwargs: Variable keyword arguments for configuration.

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
        """Retrieve an attribute by name.

        Args:
            nome (str): The name of the attribute to retrieve.

        Returns:
            TypeHint: The value of the requested attribute.

        """
        item = self.kwrgs.get(nome, None)

        if not item:
            item = CrawJUD.__dict__.get(nome, None)

            if not item:
                item = PropertiesCrawJUD.kwrgs_.get(nome, None)

        return item

    def setup(self) -> None:
        """Set up the bot by loading configuration and preparing the environment.

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

        """
        self.row = 0

        try:
            self.message = "Inicializando robô"
            self.type_log = "log"
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
        """Authenticate the bot using the specified login method.

        This method checks if the bot is logged in using the provided authentication method.
        If the login is successful, it logs a success message.
        If the login fails, it quits the driver, logs an error message, and raises an exception.

        Raises:
            ErroDeExecucao: If the login fails.

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
            logger.exception(err)
            self.row = 0
            self.message = "Erro ao realizar login"
            self.type_log = "error"

            self.prt()
            self.end_prt("Falha ao iniciar")
            if self.driver:
                self.driver.quit()

            raise e
