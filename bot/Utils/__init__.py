import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import Timestamp
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from ..common import ErroDeExecucao
from ..shared import PropertiesCrawJUD
from .auth import AuthBot
from .count_doc import count_doc
from .Driver import SetupDriver
from .elements import ElementsBot
from .interator import Interact
from .MakeTemplate import MakeXlsx
from .PrintLogs import printbot
from .search import SeachBot

__all__ = [
    AuthBot,
    MakeXlsx,
    ElementsBot,
    Interact,
    SetupDriver,
    SeachBot,
    count_doc,
    printbot,
]


class OtherUtils(PropertiesCrawJUD):

    @classmethod
    def select2elaw(cls, elementSelect: str, to_Search: str) -> None:

        selector: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, elementSelect))
        )

        items = selector.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        elementsSelecting = elementSelect.replace("'", "'")
        if '"' in elementsSelecting:
            elementsSelecting = elementSelect.replace('"', "'")

        for item in items:

            value_item = item.get_attribute("value")
            cms = f"{elementsSelecting} > option[value='{value_item}']"
            text_item = cls.driver.execute_script(f'return $("{cms}").text();')

            opt_itens.update({text_item.upper(): value_item})

        value_opt = opt_itens.get(to_Search.upper())

        if value_opt:

            command = f"$('{elementSelect}').val(['{value_opt}']);"
            command2 = f"$('{elementSelect}').trigger('change');"

            if "'" in elementSelect:
                command = f"$(\"{elementSelect}\").val(['{value_opt}']);"
                command2 = f"$(\"{elementSelect}\").trigger('change');"

            cls.driver.execute_script(command)
            cls.driver.execute_script(command2)

    def dataFrame(cls) -> list[dict[str, str]]:
        """
        Converts an Excel file to a list of dictionaries with formatted data.
        This method reads an Excel file specified by the instance's path arguments,
        processes the data by formatting dates and floats, and returns the data as
        a list of dictionaries.
        Returns:
            list[dict[str, str]]: A list of dictionaries where each dictionary
            represents a row in the Excel file with formatted data.
        Raises:
            FileNotFoundError: If the specified Excel file does not exist.
            ValueError: If there is an issue reading the Excel file.
        """

        input_file = Path(cls.path_args).joinpath(cls.xlsx).resolve()

        df = pd.read_excel(input_file)
        df.columns = df.columns.str.upper()

        for col in df.columns.to_list():
            df[col] = df[col].apply(
                lambda x: (
                    x.strftime("%d/%m/%Y")
                    if type(x) is datetime or type(x) is Timestamp
                    else x
                )
            )

        for col in df.select_dtypes(include=["float"]).columns.to_list():
            df[col] = df[col].apply(lambda x: "{:.2f}".format(x).replace(".", ","))

        vars_df = []

        df_dicted = df.to_dict(orient="records")
        for item in df_dicted:
            for key, value in item.items():
                if str(value) == "nan":
                    item.update({key: None})

            vars_df.append(item)

        return vars_df

    # @profile(stream=fp)
    def elawFormats(cls, data: dict[str, str]) -> dict[str, str]:
        """
        Formats the given data dictionary according to specific rules.
        Args:
            data (dict[str, str]): A dictionary containing key-value pairs to be formatted.
        Returns:
            dict[str, str]: The formatted dictionary.
        Rules:
            - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
            - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
            - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
            - If the value is an integer or float, format it to two decimal places and replace the decimal point with a comma.
            - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".
        """

        data_listed = list(data.items())
        for key, value in data_listed:

            if not value.strip():
                data.pop(key)

            if key.upper() == "TIPO_EMPRESA":
                data.update({"TIPO_PARTE_CONTRARIA": "Autor"})
                if value.upper() == "RÉU":
                    data.update({"TIPO_PARTE_CONTRARIA": "Autor"})

            elif key.upper() == "COMARCA":
                set_locale = cls.cities_Amazonas().get(value, None)
                if not set_locale:
                    set_locale = "Outro Estado"

                data.update({"CAPITAL_INTERIOR": set_locale})

            elif key == "DATA_LIMITE" and not data.get("DATA_INICIO"):
                data.update({"DATA_INICIO": value})

            elif type(value) is int or type(value) is float:
                data.update({key: "{:.2f}".format(value).replace(".", ",")})

            elif key == "CNPJ_FAVORECIDO" and not value:
                data.update({key: "04.812.509/0001-90"})

        return data

    # @profile(stream=fp)
    def calc_time(cls) -> list:
        """
        Calculate the elapsed time since the start time and return it as a list of minutes and seconds.
        Returns:
            list: A list containing two integers:
                - minutes (int): The number of minutes of the elapsed time.
                - seconds (int): The number of seconds of the elapsed time.
        """

        end_time = time.perf_counter()
        execution_time = end_time - cls.start_time
        calc = execution_time / 60
        splitcalc = str(calc).split(".")
        minutes = int(splitcalc[0])
        seconds = int(float(f"0.{splitcalc[1]}") * 60)

        return [minutes, seconds]

    # @profile(stream=fp)
    def append_moves(cls) -> None:
        """
        Appends movements to the spreadsheet if there are any movements to append.
        This method checks if there are any movements stored in the `cls.appends` list.
        If there are, it iterates over each movement and calls the `cls.append_success`
        method to save the movement to the spreadsheet with a success message.
        Raises:
            ErroDeExecucao: If no movements are found in the `cls.appends` list.
        """

        if len(cls.appends) > 0:

            for append in cls.appends:

                cls.append_success(
                    append, "Movimentação salva na planilha com sucesso!!"
                )

        elif len(cls.appends) == 0:
            raise ErroDeExecucao("Nenhuma Movimentação encontrada")

    # @profile(stream=fp)
    def append_success(cls, data, message: str = None, fileN: str = None):

        if not message:
            message = "Execução do processo efetuada com sucesso!"

        def save_info(data: list[dict[str, str]]):

            output_success = cls.path

            chk_not_path = output_success is None

            if fileN is not None or chk_not_path:
                output_success = Path(cls.path).parent.resolve().joinpath(fileN)

            if not output_success.exists():
                df = pd.DataFrame(data)
                df = df.to_dict(orient="records")

            elif output_success.exists():

                df = pd.read_excel(output_success)
                df = df.to_dict(orient="records")
                df.extend(data)

            new_data = pd.DataFrame(df)
            new_data.to_excel(output_success, index=False)

        typeD = type(data) is list and all(isinstance(item, dict) for item in data)

        if not typeD:

            data2 = {}

            for item in cls.name_colunas:
                data2.update({item: ""})

            for item in data:
                for key, value in list(data2.items()):
                    if not value:
                        data2.update({key: item})
                        break

            data.clear()
            data.append(data2)

        save_info(data)

        if message:
            if cls.type_log == "log":
                cls.type_log = "success"

            cls.message = message
            cls.prt()
