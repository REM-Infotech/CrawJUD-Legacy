import json
import pathlib
import platform
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import environ, path
from pathlib import Path
from typing import List, Tuple

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from ...core import (
    BarColumn,
    CrawJUD,
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
)

try:
    from getchromeVer import chrome_ver

except ModuleNotFoundError:
    from .getchromeVer import chrome_ver


class DriverBot(CrawJUD):
    def __init__(
        self,
    ) -> None:
        """"""

    list_args_ = [
        "--ignore-ssl-errors=yes",
        "--ignore-certificate-errors",
        "--display=:99",
        "--window-size=1600,900",
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--kiosk-printing",
    ]

    @property
    def list_args(self) -> List[str]:
        return self.list_args_

    @list_args.setter
    def list_args(self, new_Args: List[str]) -> None:
        self.list_args_ = new_Args

    def DriverLaunch(
        self, message: str = "Inicializando WebDriver"
    ) -> Tuple[WebDriver, WebDriverWait]:
        try:
            pid_path = self.output_dir_path.resolve()

            self.message = message
            self.type_log = "log"
            self.prt()

            list_args = self.list_args

            chrome_options = Options()
            self.chr_dir = Path(pid_path).joinpath("chrome").resolve()

            user = environ.get(
                "USER", environ.get("LOGNAME", environ.get("USERNAME", "root"))
            )
            if user != "root" or platform.system() != "Linux":
                list_args.remove("--no-sandbox")

            if platform.system() == "Windows" and self.login_method == "cert":
                state = str(self.state)
                self.path_accepted = Path(
                    path.join(
                        Path(__file__).cwd().resolve(),
                        "Browser",
                        state,
                        self.username,
                        "chrome",
                    )
                )
                path_exist = self.path_accepted.exists()
                if path_exist:
                    for root, _, files in self.path_accepted.walk():
                        try:
                            shutil.copytree(root, self.chr_dir)
                        except Exception as e:
                            print(e)

                elif not path_exist:
                    self.path_accepted.mkdir(parents=True, exist_ok=True)

            # chrome_options.add_argument(f"user-data-dir={str(self.chr_dir)}")
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
                "printing.print_preview_sticky_settings.appState": json.dumps(
                    self.settings
                ),
                "download.default_directory": "{}".format(str(pid_path)),
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

            driver = webdriver.Chrome(
                service=Service(path_chrome), options=chrome_options
            )

            # driver.maximize_window()

            wait = WebDriverWait(driver, 20, 0.01)
            driver.delete_all_cookies()

            self.message = "WebDriver inicializado"
            self.type_log = "log"
            self.prt()

            return (
                driver,
                wait,
            )

        except Exception as e:
            raise e


class SetupDriver:
    @property
    def code_ver(self) -> str:
        return ".".join(chrome_ver().split(".")[:-1])

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

    current_app_progress = Progress(
        TimeElapsedColumn(),
        TextColumn("{task.description}"),
    )

    progress_group = Group(Panel(Group(current_app_progress, progress)))

    def __init__(
        self, destination: Path = Path(__file__).cwd().resolve(), **kwrgs
    ) -> None:
        new_stem = f"chromedriver{self.code_ver}.zip"
        self.file_path = (
            pathlib.Path(__file__)
            .parent.cwd()
            .resolve()
            .joinpath("webdriver")
            .joinpath("chromedriver")
            .with_stem(new_stem)
        )

        if platform.system() == "Linux":
            self.file_path = self.file_path.with_suffix("")
            self.fileN = self.file_path.name

        elif platform.system() == "Windows":
            self.file_path = self.file_path.with_suffix(".exe")
            self.fileN = self.file_path.name

        for key, value in list(kwrgs.items()):
            setattr(self, key, value)

        self.destination = destination

    def __call__(self) -> str:
        with Live(self.progress_group):
            with ThreadPoolExecutor() as pool:
                self.ConfigBar(pool)

        shutil.copy(self.file_path, self.destination)
        return self.destination.name

    def ConfigBar(self, pool: ThreadPoolExecutor):
        self.current_task_id = self.current_app_progress.add_task(
            "[bold blue] Baixando Chromedriver"
        )
        task_id = self.progress.add_task(
            "download", filename=self.fileN.upper(), start=False
        )

        self.destination = self.destination.joinpath(self.fileN).resolve()
        root_path = Path(self.file_path).parent.resolve()
        if not self.file_path.exists():
            if not root_path.exists():
                root_path.mkdir(exist_ok=True, parents=True)

            url = self.getUrl()
            pool.submit(self.copy_url, task_id, url, self.file_path)

        elif root_path.exists():
            if self.file_path.exists():
                self.current_app_progress.update(
                    self.current_task_id,
                    description="[bold green] Carregado webdriver salvo em cache!",
                )
                shutil.copy(self.file_path, self.destination)

    def getUrl(self) -> str:
        # Verifica no endpoint qual a versão disponivel do WebDriver
        url_chromegit = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{self.code_ver}"
        results = requests.get(url_chromegit, timeout=60)
        chrome_version = results.text

        system = platform.system().replace("dows", "").lower()
        arch = platform.architecture()
        if type(arch) is tuple:
            arch = arch[0].replace("bit", "")

        os_sys = f"{system}{arch}"
        # Baixa o WebDriver conforme disponivel no repositório
        url_driver = "storage.googleapis.com/chrome-for-testing-public/"

        set_URL = [chrome_version, os_sys, os_sys]
        for pos, item in enumerate(set_URL):
            if pos == len(set_URL) - 1:
                url_driver += f"chromedriver-{item}.zip"
                continue

            url_driver += f"{item}/"

        with open("is_init.txt", "w") as f:
            f.write(url_driver)

        return url_driver

    def copy_url(self, task_id: TaskID, url: str, path: Path) -> None:
        """Copy data from a url to a local file."""

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

                not_Cr1 = member.split("/")[-1].lower() == "chromedriver.exe"
                not_Cr2 = member.split("/")[-1].lower() == "chromedriver"

                if not_Cr1 or not_Cr2:
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
        self.current_app_progress.update(
            self.current_task_id, description="[bold green] ChromeDriver Baixado!"
        )
