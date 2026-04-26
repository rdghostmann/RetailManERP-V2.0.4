# Excel Exporter Utility
import os
import pandas as pd
from openpyxl import load_workbook


class ExcelExporter:
    """
    Enterprise Excel Export Engine
    - One file
    - Multiple sheets
    - Safe overwrite per sheet
    """

    def __init__(self, file_path="RetailMan_Reports.xlsx"):
        self.file_path = file_path

    def export_sheet(self, sheet_name: str, dataframe: pd.DataFrame):
        """
        Creates or replaces a sheet in the same workbook.
        """

        # Ensure file exists or create base workbook
        if not os.path.exists(self.file_path):
            with pd.ExcelWriter(self.file_path, engine="openpyxl") as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        # Load workbook
        book = load_workbook(self.file_path)

        with pd.ExcelWriter(
            self.file_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:

            writer.book = book
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)