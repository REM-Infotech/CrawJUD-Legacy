"""Module for managing document downloads from the ELAW system.

This module handles automated document downloads from the ELAW system, including file
management, renaming, and organization of downloaded content.

Classes:
    Download: Manages document downloads by extending the CrawJUD base class
"""

import os
import shutil
from pathlib import Path
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from bots.controller.elaw import ElawBot
from bots.resources.elements import elaw as el
from common.exceptions import ExecutionError


class Download(ElawBot):
    """The Download class extends CrawJUD to handle download tasks within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


    """

    def execution(self) -> None:
        """Execute the download process."""
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            try:
                self.queue()

            except ExecutionError as e:
                message_error = str(e)

                self.print_message(
                    message=f"{message_error}.",
                    message_type="error",
                )

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(data_save=[self.bot_data])

        self.finalizar_execucao()

    def queue(self) -> None:
        """Handle the download queue processing.

        Raises:
            ExecutionError: If an error occurs during queue processing.

        """
        try:
            search = self.search()
            if search is True:
                self.message = "Processo encontrado!"
                self.message_type = "log"
                self.prt()
                self.buscar_doc()
                self.download_docs()
                self.message = "Arquivos salvos com sucesso!"
                self.append_success(
                    [
                        self.bot_data.get("NUMERO_PROCESSO"),
                        self.message,
                        self.list_docs,
                    ],
                    "Arquivos salvos com sucesso!",
                )

            elif not search:
                message_error = "Processo não encontrado!"

                self.print_message(
                    message=f"{message_error}.",
                    message_type="error",
                )

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(data_save=[self.bot_data])

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def buscar_doc(self) -> None:
        """Access the attachments page."""
        self.message = "Acessando página de anexos"
        self.message_type = "log"
        self.prt()
        anexosbutton = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.anexosbutton_css,
            )),
        )
        anexosbutton.click()
        sleep(1.5)
        self.message = "Acessando tabela de documentos"
        self.message_type = "log"
        self.prt()

    def download_docs(self) -> None:
        """Download the documents."""
        table_doc = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_table_doc,
            )),
        )
        table_doc = table_doc.find_elements(By.TAG_NAME, "tr")

        if "," in self.bot_data.get("TERMOS"):
            termos = (
                str(self.bot_data.get("TERMOS"))
                .replace(", ", ",")
                .replace(" ,", ",")
                .split(",")
            )

        elif "," not in self.bot_data.get("TERMOS"):
            termos = [str(self.bot_data.get("TERMOS"))]

        self.message = f'Buscando documentos que contenham "{self.bot_data.get("TERMOS").__str__().replace(",", ", ")}"'
        self.message_type = "log"
        self.prt()

        for item in table_doc:
            item = item
            get_name_file = str(
                item.find_elements(By.TAG_NAME, "td")[3]
                .find_element(By.TAG_NAME, "a")
                .text,
            )

            for termo in termos:
                if str(termo).lower() in get_name_file.lower():
                    sleep(1)

                    self.message = (
                        f'Arquivo com termo de busca "{termo}" encontrado!'
                    )
                    self.message_type = "log"
                    self.prt()

                    baixar = item.find_elements(By.TAG_NAME, "td")[
                        13
                    ].find_element(
                        By.CSS_SELECTOR,
                        el.botao_baixar,
                    )
                    baixar.click()

                    self.rename_doc(get_name_file)
                    self.message = "Arquivo baixado com sucesso!"
                    self.message_type = "info"
                    self.prt()

    def rename_doc(self, namefile: str) -> None:
        """Rename the downloaded document.

        Args:
            namefile (str): The new name for the file.

        """
        filedownloaded = False
        while True:
            for _, __, files in Path(self.output_dir_path).walk():
                for file in files:
                    if file.replace(" ", "") == namefile.replace(
                        " ",
                        "",
                    ):
                        filedownloaded = True
                        namefile = file
                        break

                if filedownloaded is True:
                    break

            old_file = Path(self.output_dir_path).joinpath(namefile)
            if old_file.exists():
                sleep(0.5)
                break

            sleep(0.01)

        file_name_replaced = f"{self.pid} - {namefile.replace(' ', '')}"
        path_renamed = os.path.joinpath(file_name_replaced)
        shutil.move(old_file, path_renamed)

        if not self.list_docs:
            self.list_docs = file_name_replaced

        elif self.list_docs:
            self.list_docs = self.list_docs + "," + file_name_replaced
