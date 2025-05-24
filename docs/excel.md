# `Excel` Class

The [`Excel`](../source/database/excel.py) class provides an interface to output pandas DataFrames to an Excel workbook using the `xlwings` library. Each instance of this class represents one Excel file.

---

## Table of Contents

- [Initialization](#initialization)
- [Methods](#methods)
  - [`_find_next_column(old_column: str, length: int) -> str`](#_find_next_columnold_column-str-length-int---str)
  - [`_generate_lookup(dfs: dict) -> dict`](#_generate_lookupdfs-dict---dict)
  - [`_prepare_sheet(sheet_name: str) -> xw.Sheet`](#_prepare_sheetsheet_name-str---xwsheet)
  - [`_output_table(sheet: xw.Sheet, df: pd.DataFrame, name: str, coordinate: str) -> None`](#_output_tablesheet-xwsheet-df-pddataframe-name-str-coordinate-str---none)
  - [`_format_sheet(sheet: xw.Sheet) -> None`](#_format_sheetsheet-xwsheet---none)
  - [`output_dfs(dfs: dict, sheet_name: str) -> None`](#output_dfsdfs-dict-sheet_name-str---none)
  - [`close() -> None`](#close---none)
- [Example Usage](#example-usage)

---

## Initialization

```python
Excel(filename: str)
```

### Parameters:
- `filename` (`str`): Path to the Excel file. Opens if exists, otherwise creates and saves a new file.

---

## Methods

### `_find_next_column(old_column: str, length: int) -> str`

Finds the next Excel column label given a starting column and number of columns to offset.

#### Parameters:
- `old_column` (`str`): Starting column (e.g., "B").
- `length` (`int`): Number of columns to offset.

#### Returns:
- `str`: New column label.

---

### `_generate_lookup(dfs: dict) -> dict`

Generates a mapping of DataFrame keys to Excel cell coordinates.

#### Parameters:
- `dfs` (`dict`): Dictionary with keys as names and values as DataFrames.

#### Returns:
- `dict`: Mapping of table names to Excel coordinates.

---

### `_prepare_sheet(sheet_name: str) -> xw.Sheet`

Creates or clears a sheet in the workbook.

#### Parameters:
- `sheet_name` (`str`): The name of the sheet to prepare.

#### Returns:
- `xw.Sheet`: The prepared sheet.

---

### `_output_table(sheet: xw.Sheet, df: pd.DataFrame, name: str, coordinate: str) -> None`

Inserts a DataFrame into the worksheet at the given coordinate and formats it as a table.

#### Parameters:
- `sheet` (`xw.Sheet`): Target worksheet.
- `df` (`pd.DataFrame`): Data to insert.
- `name` (`str`): Table name.
- `coordinate` (`str`): Starting cell (e.g., "B2").

#### Side Effects:
- Writes the DataFrame.
- Formats it as a table.
- Applies number formatting (`0.0`) and disables auto-filters.

---

### `_format_sheet(sheet: xw.Sheet) -> None`

Applies formatting to the used range of the worksheet.

#### Parameters:
- `sheet` (`xw.Sheet`): The worksheet to format.

#### Side Effects:
- Sets column width to 20.
- Left-aligns cell content.

---

### `output_dfs(dfs: dict, sheet_name: str) -> None`

Outputs multiple DataFrames into the specified worksheet with auto-layout and formatting.

#### Parameters:
- `dfs` (`dict`): Dictionary of table names and DataFrames.
- `sheet_name` (`str`): Name of the worksheet to write to.

#### Side Effects:
- Clears or creates the sheet.
- Writes each DataFrame to a unique cell range.
- Formats the entire sheet.

---

### `close() -> None`

Closes the workbook.

---

## Example Usage

```python
from source.database import Excel

excel = Excel("output_file.xlsm")
excel.output_dfs(dataframes_dict, "output_sheet")
excel.close()
```

---