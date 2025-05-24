# `NDPDepthChart` Class

The [`NDPDepthChart`](../source/depth_chart/ndp.py) class provides functionality for importing and organizing offensive NFL depth chart data for a specific week in a given season. Unlike `ESPNDepthChart`, this class uses the `nfl_data_py` package to source its data and is designed to be run programmatically on demand.

---

## Table of Contents

- [Initialization](#initialization)
- [Methods](#methods)
  - [`_load() -> pd.DataFrame`](#_load---pddataframe)
  - [`_group_players_by_position(group: pd.DataFrame) -> dict`](#_group_players_by_positiongroup-pddataframe---dict)
  - [`_build_position_rows(position_players: dict) -> list`](#_build_position_rowsposition_players-dict---list)
  - [`run() -> None`](#run---None)
- [Example Usage](#example-usage)

---

## Initialization

```python
NDPDepthChart(seasons: list, week: int)
```

### Parameters:
- `seasons` (`list`): A list of seasons (e.g., `[2023]`) to retrieve depth chart data for.
- `week` (`int`): The specific week of the season to extract offensive depth charts.

---

## Methods

### `_load() -> pd.DataFrame`

Loads and filters the offensive depth chart data for the given seasons and week, then processes it by adding a `full_name` column.

#### Returns:
- `pd.DataFrame`: A DataFrame of offensive depth chart entries with team, position, and player name information.

---

### `_group_players_by_position(group: pd.DataFrame) -> dict`

Groups a team's players by their position and returns a dictionary mapping positions to ordered lists of player names.

#### Parameters:
- `group` (`pd.DataFrame`): Subset of the master depth chart for a specific team.

#### Returns:
- `dict[str, list[str]]`: Dictionary with positions as keys and player name lists as values.

---

### `_build_position_rows(position_players: dict) -> list`

Converts a dictionary of position-player mappings into a list of dictionaries with starter, 2nd, and 3rd string players.

#### Parameters:
- `position_players` (`dict[str, list[str]]`): Grouped players by position.

#### Returns:
- `list[dict]`: List of dictionaries suitable for creating a structured DataFrame by position.

---

### `run() -> None`

Generates structured depth charts for all teams by grouping and transforming the master depth chart.

---

## Example Usage

```python
from source.depth_chart.ndp import NDPDepthChart
from source.database.excel import Excel

ndp = NDPDepthChart([2023], 1)
excel = Excel("output_file.xlsm")
excel.output_dfs(ndp.run(), "output_sheet")
excel.close()
```

---