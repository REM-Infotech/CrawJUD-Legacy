from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
import time
from typing import Dict, Union
from pandas import Timestamp
from dotenv import load_dotenv

# from memory_profiler import profile
import pandas as pd
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from ..common import ErroDeExecucao

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = Dict[str, Union[TypeValues, Numbers]]

# fp = open("memory_profiler_self.log", "+w")

load_dotenv()


class BasePropertiesCrawJUD:

    appends_ = []
    another_append_ = []

    path_accepted_: str = ""
    vara_: str = ""
    _system: str = ""
    _state_or_client_: str = ""
    _type_log: str = "info"
    _message: str = ""
    _pid: str = ""
    kwrgs_: Dict[str, Union[TypeValues, SubDict]] = {}
    row_: int = 0
    message_error_: str = ""
    bot_data_: Dict[str, Union[TypeValues, SubDict]] = {}
    graphicMode_: str = "doughnut"
    out_dir: str = ""
    user_data_dir: str = ""
    cr_list_args: list[str] = []
    drv: WebDriver = None
    wt: WebDriverWait = None
    elmnt = None
    interact_ = None

    @property
    # @profile(stream=fp)
    def appends(self):
        return self.appends_

    @appends.setter
    # @profile(stream=fp)
    def appends(self, new_appends: list):
        self.appends_ = new_appends

    @property
    # @profile(stream=fp)
    def another_append(self):
        return self.another_append_

    @another_append.setter
    # @profile(stream=fp)
    def another_append(self, new_another_append: list):
        self.another_append_ = new_another_append

    @property
    # @profile(stream=fp)
    def system(self):
        return self._system

    @system.setter
    # @profile(stream=fp)
    def system(self, system_: str):
        self._system = system_

    @property
    # @profile(stream=fp)
    def state_or_client(self):
        return self._state_or_client_

    @state_or_client.setter
    # @profile(stream=fp)
    def state_or_client(self, new_s: str):
        self._state_or_client_ = new_s

    @property
    # @profile(stream=fp)
    def type_log(self):
        return self._type_log

    @type_log.setter
    # @profile(stream=fp)
    def type_log(self, new_log: str):
        self._type_log = new_log

    @property
    # @profile(stream=fp)
    def pid(self) -> int:
        return self._pid

    @pid.setter
    # @profile(stream=fp)
    def pid(self, pid_) -> int:
        self._pid = pid_

    @property
    # @profile(stream=fp)
    def message(self) -> str:
        return self._message

    @message.setter
    # @profile(stream=fp)
    def message(self, new_msg: str) -> str:
        self._message = new_msg

    @property
    # @profile(stream=fp)
    def isStoped(self):
        chk = os.path.exists(os.path.join(self.output_dir_path, f"{self.pid}.flag"))
        return chk

    @property
    # @profile(stream=fp)
    def driver(self) -> WebDriver:  # pragma: no cover
        return self.drv

    @driver.setter
    # @profile(stream=fp)
    def driver(self, new_drv: WebDriver):  # pragma: no cover
        self.drv = new_drv

    @property
    # @profile(stream=fp)
    def wait(self) -> WebDriverWait:  # pragma: no cover
        return self.wt

    @wait.setter
    # @profile(stream=fp)
    def wait(self, new_wt: WebDriverWait):  # pragma: no cover
        self.wt = new_wt

    @property
    # @profile(stream=fp)
    def chr_dir(self):
        return self.user_data_dir

    @chr_dir.setter
    # @profile(stream=fp)
    def chr_dir(self, new_dir: str):
        self.user_data_dir = new_dir

    @property
    # @profile(stream=fp)
    def output_dir_path(self):
        return self.out_dir

    @output_dir_path.setter
    # @profile(stream=fp)
    def output_dir_path(self, new_outdir: str):
        self.out_dir = new_outdir

    @property
    # @profile(stream=fp)
    def kwrgs(self) -> dict:
        return self.kwrgs_

    @kwrgs.setter
    # @profile(stream=fp)
    def kwrgs(self, new_kwg):
        self.kwrgs_ = new_kwg

    @property
    # @profile(stream=fp)
    def row(self) -> int:
        return self.row_

    @row.setter
    # @profile(stream=fp)
    def row(self, new_row: int):
        self.row_ = new_row

    @property
    # @profile(stream=fp)
    def message_error(self) -> str:
        return self.message_error_

    @message_error.setter
    # @profile(stream=fp)
    def message_error(self, nw_m: str) -> str:
        self.message_error_ = nw_m

    @property
    # @profile(stream=fp)
    def graphicMode(self):
        return self.graphicMode_

    @graphicMode.setter
    # @profile(stream=fp)
    def graphicMode(self, new_graph):
        self.graphicMode_ = new_graph

    @property
    # @profile(stream=fp)
    def list_args(self):  # pragma: no cover
        return [
            "--ignore-ssl-errors=yes",
            "--ignore-certificate-errors",
            "--display=:99",
            "--window-size=1600,900",
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--kiosk-printing",
        ]

    @list_args.setter
    # @profile(stream=fp)
    def list_args(self, new_Args: list[str]):  # pragma: no cover
        self.cr_list_args = new_Args

    @property
    # @profile(stream=fp)
    def bot_data(self) -> dict[str, str | Numbers]:
        return self.bot_data_

    @bot_data.setter
    # @profile(stream=fp)
    def bot_data(self, new_botdata: dict[str, str | Numbers]):
        self.bot_data_ = new_botdata

    @property
    # @profile(stream=fp)
    def vara(self) -> str:  # pragma: no cover
        return self.vara_

    @vara.setter
    # @profile(stream=fp)
    def vara(self, vara_str: str):
        self.vara_ = vara_str

    @property
    # @profile(stream=fp)
    def path_accepted(self):
        return self.path_accepted_

    @path_accepted.setter
    # @profile(stream=fp)
    def path_accepted(self, new_path: str):
        self.path_accepted_ = new_path

    def dataFrame(self) -> list[dict[str, str]]:
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

        input_file = os.path.join(
            Path(self.path_args).parent.resolve().__str__(), str(self.xlsx)
        )

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
    def elawFormats(self, data: dict[str, str]) -> dict[str, str]:
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
                set_locale = self.cities_Amazonas().get(value, None)
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
    def calc_time(self) -> list:
        """
        Calculate the elapsed time since the start time and return it as a list of minutes and seconds.
        Returns:
            list: A list containing two integers:
                - minutes (int): The number of minutes of the elapsed time.
                - seconds (int): The number of seconds of the elapsed time.
        """

        end_time = time.perf_counter()
        execution_time = end_time - self.start_time
        calc = execution_time / 60
        splitcalc = str(calc).split(".")
        minutes = int(splitcalc[0])
        seconds = int(float(f"0.{splitcalc[1]}") * 60)

        return [minutes, seconds]

    # @profile(stream=fp)
    def append_moves(self) -> None:
        """
        Appends movements to the spreadsheet if there are any movements to append.
        This method checks if there are any movements stored in the `self.appends` list.
        If there are, it iterates over each movement and calls the `self.append_success`
        method to save the movement to the spreadsheet with a success message.
        Raises:
            ErroDeExecucao: If no movements are found in the `self.appends` list.
        """

        if len(self.appends) > 0:

            for append in self.appends:

                self.append_success(
                    append, "Movimentação salva na planilha com sucesso!!"
                )

        elif len(self.appends) == 0:
            raise ErroDeExecucao("Nenhuma Movimentação encontrada")

    # @profile(stream=fp)
    def append_success(self, data, message: str = None, fileN: str = None):

        if not message:
            message = "Execução do processo efetuada com sucesso!"

        def save_info(data: list[dict[str, str]]):

            output_success = self.path

            chk_not_path = output_success is None or output_success == ""

            if fileN is not None or chk_not_path:
                output_success = os.path.join(Path(self.path).parent.resolve(), fileN)

            if not os.path.exists(output_success):
                df = pd.DataFrame(data)
                df = df.to_dict(orient="records")

            elif os.path.exists(output_success):

                df = pd.read_excel(output_success)
                df = df.to_dict(orient="records")
                df.extend(data)

            new_data = pd.DataFrame(df)
            new_data.to_excel(output_success, index=False)

        typeD = type(data) is list and all(isinstance(item, dict) for item in data)

        if not typeD:

            data2 = {}

            for item in self.name_colunas:
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
            if self.type_log == "log":
                self.type_log = "success"

            self.message = message
            self.prt()


class PropertiesCrawJUD(BasePropertiesCrawJUD):
    def __init__(self, *args, **kwrgs) -> None:
        super().__init__(*args, **kwrgs)
