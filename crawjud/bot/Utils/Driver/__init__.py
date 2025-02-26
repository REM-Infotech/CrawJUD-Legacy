"""Module for managing WebDriver instances and related utilities."""

from __future__ import annotations

import json
import logging
import platform
import shutil
import traceback
import zipfile
from collections.abc import Mapping  # noqa: F401
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import getenv, path
from pathlib import Path
from time import sleep  # noqa: F401
from uuid import uuid4

import requests
from selenium.common.exceptions import WebDriverException  # noqa: F401
from selenium.webdriver.remote.webdriver import WebDriver

from ...core import (
    BarColumn,
    Chrome,
    CrawJUD,
    DownloadColumn,
    Group,
    Live,
    Options,
    Panel,
    Progress,
    Service,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    WebDriverWait,
)

if __name__ == "__main__":
    from getchrome_version import another_chrome_ver, chrome_ver
else:
    from .getchrome_version import another_chrome_ver, chrome_ver  # noqa: F401

import socket

default_dir = Path(__file__).cwd().resolve()
logger = logging.getLogger(__name__)
# from typing import list, tuple
_is_connectable_exceptions = (socket.error, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError)


# class CustomService(Service):
#     """Custom service class that is responsible for the starting and stopping of `chromedriver`."""

#     def __init__(
#         self,
#         executable_path: str = None,
#         port: int = 0,
#         service_args: list = None,
#         log_output: int = None,
#         env: Optional[Mapping[str, str]] = None,
#         **kwargs: dict[str, any],
#     ) -> None:
#         """
#         Service class that is responsible for the starting and stopping of `chromedriver`.

#         Args:
#             executable_path (str, optional): install path of the chromedriver executable, defaults to `chromedriver`.
#             port (int, optional): Port for the service to run on, defaults to 0 where the operating system will decide
#             service_args (list, optional): List of args to be passed to the subprocess when launching the executable.
#             log_output (int, optional): int representation of STDOUT/DEVNULL, any IO instance or String path to file.
#             env (Optional[Mapping[str, str]], optional): Mapping of environment variables, defaults to `os.environ`.
#             **kwargs: Additional keyword arguments.

#         """
#         super().__init__(executable_path, port, service_args, log_output, env, **kwargs)

#     def start(self) -> None:
#         """Start the Service.

#         Raises:
#             WebDriverException: Raised either when it can't start the service
#            or when it can't connect to the service

#         """
#         if self._path is None:
#             raise WebDriverException("Service path cannot be None.")
#         self._start_process(self._path)

#         count = 0
#         while True:
#             self.assert_process_still_running()
#             if self.is_connectable():
#                 break
#             # sleep increasing: 0.01, 0.06, 0.11, 0.16, 0.21, 0.26, 0.31, 0.36, 0.41, 0.46, 0.5
#             sleep(min(0.01 + 0.05 * count, 0.5))
#             count += 1
#             if count == 70:
#                 raise WebDriverException(f"Can not connect to the Service {self._path}")

#     def is_connectable(self, host: Optional[str] = "127.0.0.1") -> bool:
#         """Try to connect to the server at port to see if it is running.

#         Args:
#             host (Optional[str], optional): The host to connect to. Defaults to "localhost".

#         """
#         socket_ = None
#         try:
#             socket_ = socket.create_connection((host, self.port), 300)
#             result = True
#         except _is_connectable_exceptions:
#             err = traceback.format_exc()
#             logger.exception(err)
#             result = False
#         finally:
#             if socket_:
#                 socket_.close()
#         return result


class DriverBot(CrawJUD):
    """Bot for handling WebDriver operations within CrawJUD framework."""

    def __init__(self) -> None:
        """
        Initialize DriverBot with default settings for WebDriver operations in CrawJUD promptly.

        Args:
            None.

        """

    list_args_ = [
        "--ignore-ssl-errors=yes",
        "--ignore-certificate-errors",
        "--display=:99",
        "--window-size=1600,900",
        # "--no-sandbox",
        "--kiosk-printing",
        # disable Render and GPU
        # "--disable-gpu",
        # "--disable-dev-shm-usage",
        # "--disable-software-rasterizer",
        # "--disable-renderer-backgrounding",
        # "--disable-backgrounding-occluded-windows",
        "--disable-blink-features=AutomationControlled",
        # "--disable-features=MediaFoundationVideoCapture",
        # disable network prediction
        # "--no-proxy-server",
        # "--disable-software-rasterizer",
        # "--disable-features=VizDisplayCompositor",
    ]

    @property
    def list_args(self) -> list[str]:
        """Get the list of arguments for WebDriver."""
        return self.list_args_

    @list_args.setter
    def list_args(self, new_args: list[str]) -> None:
        """Set a new list of arguments for WebDriver.

        Args:
            new_args (list[str]): The new arguments to set.

        """
        self.list_args_ = new_args

    def driver_launch(self, message: str = "Inicializando WebDriver") -> tuple[WebDriver, WebDriverWait]:
        """
        Launch WebDriver with options and extensions, then return driver and wait to run well.

        Args:
            message (str, optional): Initialization message.

        Returns:
            tuple[WebDriver, WebDriverWait]: The launched driver and its wait instance.

        Raises:
            Exception: Propagates any exception raised during driver launch.

        """
        try:
            pid_path = self.output_dir_path.resolve()

            self.message = message
            self.type_log = "log"
            self.prt()

            list_args = self.list_args

            chrome_options = Options()

            chrome_options.binary_location = getenv("CHROME_EXECUTABLE")

            self.logger.info("Chrome Executable: %s", chrome_options.binary_location)

            self.chr_dir = Path(pid_path).joinpath("chrome").resolve()

            if platform.system() == "Windows" and self.login_method == "cert":
                state = str(self.state)
                self.path_accepted = Path(
                    path.join(Path(__file__).cwd().resolve(), "Browser", state, self.username, "chrome"),
                )
                path_exist = self.path_accepted.exists()
                if path_exist:
                    for root, _, __ in self.path_accepted.walk():
                        try:
                            shutil.copytree(root, self.chr_dir)
                        except Exception:
                            err = traceback.format_exc()
                            logger.exception(err)

                elif not path_exist:
                    self.path_accepted.mkdir(parents=True, exist_ok=True)

            usr_dt_dir = Path(__file__).cwd().joinpath("temp").joinpath(uuid4().hex).joinpath("chrome")
            usr_dt_dir.mkdir(parents=True, exist_ok=True)

            # chrome_options.add_argument(f"user-data-dir={str(usr_dt_dir)}")
            for argument in list_args:
                chrome_options.add_argument(argument)

            this_path = Path(__file__).parent.resolve().joinpath("extensions")
            for root, _, files in this_path.walk():
                for file_ in files:
                    if ".crx" in file_:
                        path_plugin = str(root.joinpath(file_).resolve())
                        chrome_options.add_extension(path_plugin)

            chrome_prefs = {
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0,
                "printing.print_preview_sticky_settings.appState": json.dumps(self.settings),
                "download.default_directory": f"{pid_path!s}",
            }

            path_chrome = None
            chrome_options.add_experimental_option("prefs", chrome_prefs)

            getdriver = SetupDriver(destination=pid_path)

            if message != "Inicializando WebDriver":
                version = getdriver.code_ver
                chrome_name = f"chromedriver{version}"
                if platform.system() == "Windows":
                    chrome_name += ".exe"

                existspath_ = Path(pid_path).joinpath(chrome_name)
                path_chrome = existspath_ if existspath_.exists() else None

            if path_chrome is None:
                path_chrome = Path(pid_path).joinpath(getdriver()).resolve()

            path_chrome.chmod(0o777, follow_symlinks=True)

            serve = Service(path_chrome)
            serve.start()
            driver = Chrome(service=serve, options=chrome_options)
            # cliente = ClientConfig(f"http://localhost:{serve.port}")
            # remote = RemoteConnection(client_config=cliente)
            # driver = WebDriver(options=chrome_options, command_executor=remote)

            wait = WebDriverWait(driver, 20, 0.01)
            driver.delete_all_cookies()

            self.message = "WebDriver inicializado"
            self.type_log = "log"
            self.prt()

            return (driver, wait)

        except Exception as e:
            raise e


class SetupDriver:
    """Utility to download and configure the appropriate WebDriver binary."""

    # another_ver = False
    # try:
    #     chrome_v = ".".join(chrome_ver().split(".")[:-1])

    # except Exception:
    #     another_ver = True
    #     chrome_v = another_chrome_ver()

    another_ver = True
    chrome_v = another_chrome_ver()
    _url_driver: str = None

    @property
    def url_driver(self) -> str:
        """Retrieve the URL for downloading the WebDriver.

        Returns:
            str: The URL for downloading the WebDriver.

        """
        return SetupDriver._url_driver

    @url_driver.setter
    def url_driver(self, url: str) -> None:
        """Set the URL for downloading the WebDriver.

        Args:
            url (str): The URL for downloading the WebDriver.

        """
        SetupDriver._url_driver = url

    @property
    def code_ver(self) -> str:
        """Retrieve the major version of the installed Chrome browser.

        Returns:
            str: The major version of the installed Chrome browser.

        """
        return SetupDriver.chrome_v

    @code_ver.setter
    def code_ver(self, version: str) -> None:
        """Set the major version of the installed Chrome browser.

        Args:
            version (str): The major version of the installed Chrome browser.

        """
        SetupDriver.chrome_v = version

    progress = Progress(
        TimeElapsedColumn(),
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )

    current_app_progress = Progress(TimeElapsedColumn(), TextColumn("{task.description}"))

    grp = Group(current_app_progress, progress)
    painel = Panel(grp)

    progress_group = Group(painel)

    def __init__(self, destination: Path = default_dir, **kwargs: dict[str, any]) -> None:
        """
        Initialize SetupDriver to download and configure the appropriate WebDriver binary aptly.

        Args:
            destination (Path, optional): Destination directory for WebDriver.
            **kwargs: Additional configuration parameters.

        """
        self.url_driver = self.get_url()
        new_stem = f"chromedriver{self.code_ver}.zip"
        root_dir = Path(__file__).parent.cwd()
        without_stem = root_dir.joinpath("crawjud/bot", "webdriver", "chromedriver")
        self.file_path = without_stem.with_stem(new_stem).resolve()

        if platform.system() == "Linux":
            self.file_path = self.file_path.with_suffix("")
            self.fileN = self.file_path.name

        elif platform.system() == "Windows":
            self.file_path = self.file_path.with_suffix(".exe")
            self.fileN = self.file_path.name

        for key, value in list(kwargs.items()):
            setattr(self, key, value)

        self.destination = destination

    def __call__(self) -> str:
        """
        Execute driver setup process, download and extract WebDriver, then copy to destination.

        Args:
            None.

        Returns:
            str: Name of the downloaded WebDriver file.

        """
        with Live(self.progress_group):
            with ThreadPoolExecutor() as pool:
                self.configure_bar(pool)

        shutil.copy(self.file_path, self.destination)
        return self.destination.name

    def configure_bar(self, pool: ThreadPoolExecutor) -> None:
        """
        Configure download progress bar for obtaining the WebDriver with ThreadPoolExecutor.

        Args:
            pool (ThreadPoolExecutor): Executor for handling parallel downloads.

        """
        self.current_task_id = self.current_app_progress.add_task("[bold blue] Baixando Chromedriver")
        task_id = self.progress.add_task("download", filename=self.fileN.upper(), start=False)

        self.destination = self.destination.joinpath(self.fileN).resolve()
        root_path = Path(self.file_path).parent.resolve()
        if not self.file_path.exists():
            if not root_path.exists():
                root_path.mkdir(exist_ok=True, parents=True)

            url = self.get_url()
            pool.submit(self.copy_url, task_id, url, self.file_path)

        elif root_path.exists():
            if self.file_path.exists():
                self.current_app_progress.update(
                    self.current_task_id,
                    description="[bold green] Carregado webdriver salvo em cache!",
                )
                shutil.copy(self.file_path, self.destination)

    def get_url(self) -> str:
        """
        Construct download URL for WebDriver based on Chrome version and system architecture.

        Args:
            None.

        Returns:
            str: Constructed URL for downloading WebDriver.

        """
        # Verifica no endpoint qual a versão disponivel do WebDriver
        if self.another_ver is True:
            l_old_v = self.code_ver.split(".")
            l_old_v.pop(-1)

            self.code_ver = ".".join(l_old_v)

        url_chromegit = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{self.code_ver}"
        results = requests.get(url_chromegit, timeout=60)
        self.code_ver = results.text

        system = platform.system().replace("dows", "").lower()
        arch = platform.architecture()
        if type(arch) is tuple:
            arch = arch[0].replace("bit", "")

        os_sys = f"{system}{arch}"
        # Baixa o WebDriver conforme disponivel no repositório
        url_driver = "storage.googleapis.com/chrome-for-testing-public/"

        set_url = [self.code_ver, os_sys, os_sys]
        for pos, item in enumerate(set_url):
            if pos == len(set_url) - 1:
                url_driver += f"chromedriver-{item}.zip"
                continue

            url_driver += f"{item}/"

        # with open("url_driver.txt", "w") as f:  # FURB103
        #     f.write(url_driver)

        return url_driver

    def copy_url(self, task_id: TaskID, url: str, path: Path) -> None:
        """
        Download, extract, and move WebDriver from URL zip file to specified path ready now.

        Args:
            task_id (TaskID): ID for progress tracking.
            url (str): URL to download from.
            path (Path): File path to save and extract WebDriver.

        """
        zip_name = path.with_name(f"{path.name}.zip")
        response = requests.get(f"https://{url}", stream=True, timeout=60)
        # input("teste")
        # This will break if the response doesn't contain content length
        self.progress.update(task_id, total=int(response.headers["Content-length"]))

        with zip_name.open("wb") as dest_file:
            self.progress.start_task(task_id)
            for data in iter(partial(response.raw.read, 32768), b""):
                dest_file.write(data)
                self.progress.update(task_id, advance=len(data))

        # input(str("member"))
        # Extract the zip file

        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            # Extract each file directly into the subfolder
            for member in zip_ref.namelist():
                # input(str(member))
                self.progress.print(member)
                self.progress.update(task_id)

                not_chrome1 = member.split("/")[-1].lower() == "chromedriver.exe"
                not_chrome2 = member.split("/")[-1].lower() == "chromedriver"

                if not_chrome1 or not_chrome2:
                    # Get the original file name without any directory structure
                    dir_name = path.name
                    extracted_path = Path(zip_ref.extract(member, dir_name))
                    base_name = extracted_path.name
                    # If the extracted path has directories, move the file directly into the subfolder
                    chk = base_name and extracted_path.is_dir()
                    if chk:
                        continue

                    shutil.move(extracted_path, path)

        zip_name.unlink()
        self.current_app_progress.update(self.current_task_id, description="[bold green] ChromeDriver Baixado!")
