import logging
import os

import pandas as pd
import xlwings as xw

logger = logging.getLogger(__name__)

class Excel:
    def __init__(self, filename: str = "nfl.xlsm"):
        self.filename = filename
        self.wb = self._load()

    def _load(self):
        try:
            if os.path.exists(self.filename):
                wb = xw.Book(self.filename)
            else:
                wb = xw.Book()
                wb.save(self.filename)
            return wb
        except Exception as e:
            logger.error(f"Error loading Excel file '{self.filename}': {e}")
            raise

    def _prepare_sheet(self, sheet_name: str) -> xw.Sheet:
        try:
            if sheet_name in [s.name for s in self.wb.sheets]:
                sheet = self.wb.sheets[sheet_name]
            else:
                sheet = self.wb.sheets.add(sheet_name)
            sheet.cells.clear()
            return sheet
        except Exception as e:
            logger.error(f"Error preparing sheet '{sheet_name}': {e}")
            raise

    def _find_next_column(self, old_column: str, length: int) -> str:
        try:
            old_index = sum((ord(char.upper()) - ord('A') + 1) * 26 ** i for i, char in enumerate(reversed(old_column)))
            next_index = old_index + length
            next_column = ""
            while next_index > 0:
                next_index, remainder = divmod(next_index - 1, 26)
                next_column = chr(remainder + ord('A')) + next_column
            return next_column
        except Exception as e:
            logger.error(f"Error finding next column from '{old_column}': {e}")
            raise

    def _generate_lookup(self, dfs: dict) -> dict:
        try:
            lookup = {}
            col = "B"
            row = 2
            for idx, (key, df) in enumerate(dfs.items()):
                if idx % 4 == 0 and idx != 0:
                    row = 2
                    col = self._find_next_column('B', (idx // 4) * (len(df.columns) + 2))
                lookup[key] = f"{col}{row}"
                row += len(df) + 2
            return lookup
        except Exception as e:
            logger.error(f"Error generating lookup for dataframes: {e}")
            raise

    def _output_table(self, sheet: xw.Sheet, df: pd.DataFrame, name: str, coordinate: str) -> None:
        try:
            sheet.range(coordinate).value = df
            data_range = sheet.range(coordinate).expand()
            table = sheet.api.ListObjects.Add(1, data_range.api, 0, 1, None)
            table.Name = name
            table.ShowAutoFilter = False
            data_range.number_format = '0.' + ('0' * 1)
        except Exception as e:
            logger.error(f"Error outputting table '{name}' at '{coordinate}': {e}")
            raise

    def _format_sheet(self, sheet: xw.Sheet) -> None:
        try:
            for c in sheet.used_range.columns:
                c.column_width = 20
            sheet.used_range.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignLeft
        except Exception as e:
            logger.error(f"Error formatting sheet: {e}")
            raise

    def output_dfs(self, dfs: dict, sheet_name: str) -> None:
        try:
            sheet = self._prepare_sheet(sheet_name)
            lookup = self._generate_lookup(dfs)
            for key, df in dfs.items():
                self._output_table(sheet, df, key, lookup[key])
            self._format_sheet(sheet)
        except Exception as e:
            logger.error(f"Error outputting dataframes to sheet '{sheet_name}': {e}")
            raise

    def close(self) -> None:
        try:
            self.wb.close()
        except Exception as e:
            logger.error(f"Error closing workbook: {e}")
            raise
        