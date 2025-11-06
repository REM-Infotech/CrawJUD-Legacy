"""Implemente funcionalidades principais do bot CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from contextlib import suppress
from threading import Event
from time import sleep
from typing import TYPE_CHECKING, ClassVar, Self

from celery import shared_task

from bots.resources.driver import BotDriver
from bots.resources.iterators import BotIterator
from bots.resources.managers.credencial_manager import CredencialManager
from bots.resources.managers.file_manager import FileManager
from bots.resources.queues.file_operation import SaveError, SaveSuccess
from bots.resources.queues.print_message import PrintMessage
from constants import WORKDIR

if TYPE_CHECKING:
    from pathlib import Path

    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait
    from seleniumwire.webdriver import Chrome

    from app.types import Dict


class CrawJUD:
    """Implemente a abstração do bot CrawJUD."""

    bots: ClassVar[dict[str, type[Self]]] = {}
    row: int = 0
    _total_rows: int = 0
    remaining: int = 0

    def __init_subclass__(cls) -> None:
        """Inicialize subclasses do CrawJUD e registre bots.

        Args:
            cls (type): Subclasse de CrawJUD.


        """
        module_split = cls.__module__.split(".")
        if (
            "master" in module_split
            or "controller" in module_split
            or len(set(module_split)) != len(module_split)
        ):
            return

        name_bot = "_".join(
            module_split[1:] if len(module_split) == 3 else module_split[2:],
        )
        if "__" in name_bot:
            return

        CrawJUD.bots[name_bot] = cls

    def setup(self, config: Dict) -> Self:
        """Configure o bot com as opções fornecidas.

        Args:
            config (Dict): Configurações do bot.

        Returns:
            Self: Instância configurada do bot.

        """
        self.config = config
        self.bot_stopped = Event()
        self.print_message = PrintMessage(self)
        self.append_success = SaveSuccess(self)
        self.append_error = SaveError(self)
        self.credenciais = CredencialManager(self)
        self.file_manager = FileManager(self)
        self.bot_driver = BotDriver(self)

        self.print_message("Robô inicializado!", message_type="success")

        if config.get("credenciais"):
            self.credenciais.load_credenciais(
                self.config.get("credenciais"),
            )
            if not self.auth():
                with suppress(Exception):
                    self.driver.quit()

        if config.get("planilha_xlsx"):
            self.file_manager.download_files()
            self.frame = BotIterator(self)

        return self

    def finalizar_execucao(self) -> None:
        """Finalize a execução do bot e faça upload dos resultados."""
        with suppress(Exception):
            self.append_success.queue_save.shutdown()
            self.append_error.queue_save.shutdown()
            window_handles = self.driver.window_handles
            if window_handles:
                self.driver.delete_all_cookies()
                self.driver.quit()

        message = "Fim da execução"
        link = self.file_manager.upload_file()
        self.print_message(
            message=message,
            message_type="success",
            link=link,
        )

        sleep(5)

        self.print_message.queue_print_bot.shutdown()

    @abstractmethod
    def execution(self) -> None:
        """Execute as ações principais do bot.

        Raises:
            NotImplementedError: Método deve ser implementado
                pelas subclasses.

        """
        ...

    @property
    def driver(self) -> WebDriver | Chrome:
        """Retorne o driver do navegador utilizado pelo bot."""
        return self.bot_driver.driver

    @property
    def wait(self) -> WebDriverWait[WebDriver | Chrome]:
        """Retorne o objeto de espera do driver do navegador."""
        return self.bot_driver.wait

    @property
    def output_dir_path(self) -> Path:
        """Retorne o caminho do diretório de saída do bot.

        Returns:
            Path: Caminho do diretório de saída criado.

        """
        out_dir = WORKDIR.joinpath("output", self.pid)
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def planilha_xlsx(self) -> str:
        """Retorne o caminho da planilha XLSX utilizada pelo bot."""
        return self.config.get("planilha_xlsx")

    @planilha_xlsx.setter
    def planilha_xlsx(self, val: str) -> None:
        self.config.update({"planilha_xlsx": val})

    @property
    def pid(self) -> str:
        """Retorne o identificador do processo do bot.

        Returns:
            str: Identificador do processo.

        """
        return self.config.get("pid")

    @property
    def anexos(self) -> list[str]:
        """Retorne a lista de anexos do bot.

        Returns:
            list[str]: Lista de caminhos dos anexos.

        """
        return self.config.get("anexos")

    @property
    def total_rows(self) -> int:
        """Retorne o total de linhas processadas pelo bot.

        Returns:
            int: Número total de linhas.

        """
        return self._total_rows

    @total_rows.setter
    def total_rows(self, value: int) -> None:
        self.remaining = value
        self._total_rows = value


@shared_task(name="crawjud")
def start_bot(config: Dict) -> None:
    """Inicie o bot CrawJUD com a configuração fornecida.

    Args:
        config (Dict): Configuração do bot.

    Returns:
        None: Não retorna valor.

    """
    bot_nome = f"{config['categoria']}_{config['sistema']}"
    bot = CrawJUD.bots[bot_nome]()
    return bot.setup(config=config).execution()
