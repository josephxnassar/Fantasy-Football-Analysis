import pandas as pd
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from source.database.excel import Excel

filename = "test.xlsx"

def test_load_existing_file(mocker: MockerFixture):
    mock_exists = mocker.patch("source.database.excel.os.path.exists", return_value=True)
    mock_book = mocker.patch("source.database.excel.xw.Book")

    Excel(filename)
    mock_exists.assert_called_once_with(filename)
    mock_book.assert_called_once_with(filename)

def test_load_new_file(mocker: MockerFixture):
    mock_exists = mocker.patch("source.database.excel.os.path.exists", return_value = False)
    mock_instance = mocker.Mock()
    mocker.patch("source.database.excel.xw.Book", return_value = mock_instance)

    Excel(filename)
    mock_exists.assert_called_once_with(filename)
    mock_instance.save.assert_called_once_with(filename)

def test_prepare_sheet_existing(mocker: MockerFixture):
    mock_sheet = mocker.Mock()
    mock_sheet.name = "mock"

    sheets_mock = MagicMock()
    sheets_mock.__iter__.return_value = [mock_sheet]
    sheets_mock.__getitem__.return_value = mock_sheet

    stats = Excel.__new__(Excel)
    stats.wb = mocker.Mock()
    stats.wb.sheets = sheets_mock

    result = stats._prepare_sheet("mock")

    mock_sheet.cells.clear.assert_called_once()
    assert result == mock_sheet

def test_prepare_sheet_new(mocker: MockerFixture):
    added_sheet = mocker.Mock()
    sheets_mock = MagicMock()
    sheets_mock.__iter__.return_value = []
    sheets_mock.add.return_value = added_sheet

    stats = Excel.__new__(Excel)
    stats.wb = mocker.Mock()
    stats.wb.sheets = sheets_mock

    result = stats._prepare_sheet("mock")

    added_sheet.cells.clear.assert_called_once()
    assert result == added_sheet

def test_find_next_column():
    stats = Excel.__new__(Excel)
    assert stats._find_next_column("A", 1) == "B"
    assert stats._find_next_column("Z", 1) == "AA"
    assert stats._find_next_column("AA", 26) == "BA"

def test_generate_lookup(mocker: MockerFixture):
    stats = Excel.__new__(Excel)
    mock_find = mocker.patch("source.database.excel.Excel._find_next_column", return_value = "E")

    dfs = {"QB": pd.DataFrame(columns=["a", "b"]),
           "RB": pd.DataFrame(columns=["a", "b"]),
           "WR": pd.DataFrame(columns=["a", "b"]),
           "TE": pd.DataFrame(columns=["a", "b"]),
           "K" : pd.DataFrame(columns=["a", "b"])}
    
    result = stats._generate_lookup(dfs)

    assert isinstance(result, dict)
    assert "QB" in result and result["K"].startswith("E")
    assert mock_find.call_count == 1

def test_output_table(mocker: MockerFixture):
    df = pd.DataFrame({"a": [1.1, 2.2], "b": [3.3, 4.4]})
    data_range = mocker.MagicMock()
    data_range.api = mocker.MagicMock()
    sheet = mocker.MagicMock()
    sheet.range.return_value = data_range
    data_range.expand.return_value = data_range

    stats = Excel.__new__(Excel)
    stats._output_table(sheet, df, "MyTable", "B2")
    assert sheet.range.call_count == 2
    assert sheet.range.call_args_list == [mocker.call("B2"), mocker.call("B2")]
    assert data_range.number_format == "0.0"

def test_format_sheet(mocker: MockerFixture):
    used_range = mocker.Mock()
    used_range.columns = [mocker.Mock(), mocker.Mock()]
    
    stats = Excel.__new__(Excel)
    sheet = mocker.Mock()
    sheet.used_range = used_range

    stats._format_sheet(sheet)
    for col in used_range.columns:
        assert col.column_width == 20
    assert used_range.api.HorizontalAlignment is not None

def test_output_dfs(mocker: MockerFixture):
    dfs = {"QB": pd.DataFrame(columns=["x"]), 
           "RB": pd.DataFrame(columns=["y"])}

    mock_sheet = mocker.Mock()
    mock_lookup = {"QB": "B2", "RB": "B10"}

    mocker.patch("source.database.excel.Excel._prepare_sheet", return_value = mock_sheet)
    mocker.patch("source.database.excel.Excel._generate_lookup", return_value = mock_lookup)
    mock_output = mocker.patch("source.database.excel.Excel._output_table")
    mock_format = mocker.patch("source.database.excel.Excel._format_sheet")

    stats = Excel.__new__(Excel)
    stats.output_dfs(dfs, "Stats")
    mock_output.assert_called()
    mock_format.assert_called_once_with(mock_sheet)

def test_close_workbook(mocker: MockerFixture):
    stats = Excel.__new__(Excel)
    stats.wb = mocker.Mock()
    stats.close()
    stats.wb.close.assert_called_once()