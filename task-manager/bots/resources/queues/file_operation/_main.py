from contextlib import suppress
from pathlib import Path
from typing import cast

from openpyxl import Workbook
from pandas import DataFrame, ExcelWriter, concat, read_excel

from app.interfaces import DataSave


class FileOperator:
    def load_writer(self, arquivo_xlsx: Path) -> ExcelWriter:
        if arquivo_xlsx.exists():
            return ExcelWriter(
                arquivo_xlsx,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="replace",
            )

        return ExcelWriter(arquivo_xlsx, engine="openpyxl")

    def save_file(self, data: DataSave, arquivo_xlsx: Path) -> None:
        with suppress(Exception):
            df = DataFrame(data["data_save"])
            writer = self.load_writer(arquivo_xlsx)
            wb = cast(Workbook, writer.book)

            # Verifica se a worksheet já existe
            if data["worksheet"] in wb.sheetnames:
                df_xlsx = read_excel(
                    arquivo_xlsx,
                    engine="openpyxl",
                    sheet_name=data["worksheet"],
                )
                df = concat([
                    DataFrame(df_xlsx.to_dict(orient="records")),
                    DataFrame(data["data_save"]),
                ])

            df.to_excel(
                excel_writer=writer,
                sheet_name=data["worksheet"],
                index=False,
            )
            writer.close()
