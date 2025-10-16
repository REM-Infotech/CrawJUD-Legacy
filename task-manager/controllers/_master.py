"""Abstração CrawJUD."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from __types import P, T
from celery import Task
from constants import WORKDIR
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome


class CrawJUD(Task):
    """Classe CrawJUD."""

    _task: Callable[P, T]

    def __init__(self) -> None:
        self._task = self.run
        self.run = self.__call__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        self.setup()
        return self._task(*args, **kwargs)

    def setup(self) -> None:
        options = ChromeOptions()
        self.driver = Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)

    def zip_result(self) -> Path:
        zip_filename = f"{self.pid[:6].upper()}.zip"
        source_dir = self.output_dir_path
        output_dir = WORKDIR.joinpath("archives", zip_filename)

        output_dir.parent.mkdir(exist_ok=True, parents=True)

        with ZipFile(output_dir, "w", ZIP_DEFLATED) as zipfile:
            for root, _, files in source_dir.walk():
                for file in files:
                    if self.pid in file and ".log" not in file:
                        file_path = root.joinpath(file)
                        arcname = file_path.relative_to(source_dir)
                        zipfile.write(file_path, arcname)

        return output_dir
