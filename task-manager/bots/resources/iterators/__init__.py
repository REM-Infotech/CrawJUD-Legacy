from datetime import datetime
from typing import Self

from pandas import Timestamp, read_excel

from __types import AnyType
from _interfaces import BotData
from bots.resources._formatadores import formata_string


class BotIterator[T]:
    def __init__(self, bot: object) -> None:
        self._index = 0
        path_xlsx = self.bot.output_dir_path.joinpath(
            formata_string(self.bot.planilha_xlsx),
        )

        with path_xlsx.open("rb") as fp:
            df = read_excel(fp, engine="openpyxl")

        df = df.to_dict(orient="records")
        df.columns = df.columns.str.upper()

        for col in df.columns:
            df[col] = df[col].apply(self.format_data)

        for col in df.select_dtypes(include=["float"]).columns:
            df[col] = df[col].apply(self.format_float)

        data_bot: list[BotData] = []
        to_dict = df.to_dict(orient="records")
        unformatted = [BotData(list(item.items())) for item in to_dict]

        for item in unformatted:
            dt = {}

            for k, v in list(item.items()):
                dt[k.upper()] = v

            if dt:
                data_bot.append(dt)

        self._frame = data_bot

    def __iter__(self) -> Self:
        """Retorne o próprio iterador para permitir iteração sobre regiões.

        Returns:
            RegioesIterator: O próprio iterador de regiões.

        """
        return self

    def __next__(self) -> T:
        """Implementa a iteração retornando próxima região e dados associados.

        Returns:
            tuple[str, str]: Tupla contendo a região e os dados da região.

        Raises:
            StopIteration: Quando todas as regiões forem iteradas.

        """
        if self._index >= len(self._frame):
            raise StopIteration

        data = self._frame[self._index]
        self._index += 1
        return data

    def format_data(self, x: AnyType) -> str:
        if str(x) == "NaT" or str(x) == "nan":
            return ""

        if isinstance(x, (datetime, Timestamp)):
            return x.strftime("%d/%m/%Y")

        return x

    def format_float(self, x: AnyType) -> str:
        return f"{x:.2f}".replace(".", ",")
