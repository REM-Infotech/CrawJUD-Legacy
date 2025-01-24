import json
import os
import pathlib
import platform
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import List

import requests
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from ...shared import PropertiesCrawJUD
from ..PrintLogs import printbot

try:
    from getchromeVer import chrome_ver

except ModuleNotFoundError:
    from .getchromeVer import chrome_ver


class DriverBot(PropertiesCrawJUD):
    prt = printbot.print_msg

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
    def list_args(self, new_Args: list[str]) -> None:
        self.list_args_ = new_Args

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
        self, destination: str = os.path.join(pathlib.Path(__file__).cwd()), **kwrgs
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
        return os.path.basename(self.destination)

    def ConfigBar(self, pool: ThreadPoolExecutor):
        self.current_task_id = self.current_app_progress.add_task(
            "[bold blue] Baixando Chromedriver"
        )
        task_id = self.progress.add_task(
            "download", filename=self.fileN.upper(), start=False
        )

        self.destination = os.path.join(self.destination, self.fileN)
        root_path = str(Path(self.file_path).parent.resolve())
        if not os.path.exists(self.file_path):

            if not os.path.exists(root_path):
                os.makedirs(root_path, mode=0o775)
            url = self.getUrl()
            pool.submit(self.copy_url, task_id, url, self.file_path)

        elif os.path.exists(root_path):
            if os.path.exists(self.file_path):
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

        zip_name.chmod(0o775)
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
                    dir_name = os.path.dirname(path)
                    extracted_path = zip_ref.extract(member, dir_name)
                    base_name = os.path.basename(extracted_path)
                    # If the extracted path has directories, move the file directly into the subfolder
                    chk = base_name and os.path.isdir(extracted_path)
                    if chk:
                        continue

                    shutil.move(extracted_path, path)
                    path.chmod(0o775)

        zip_name.unlink()
        self.current_app_progress.update(
            self.current_task_id, description="[bold green] ChromeDriver Baixado!"
        )
