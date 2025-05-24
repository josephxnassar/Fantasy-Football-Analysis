# `Statistics` Class

The [`Statistics`](../source/statistics/statistics.py) class provides functionality for importing, processing, and analyzing NFL seasonal data. It performs key operations such as loading player data, partitioning by player positions, filtering statistics columns, and creating player ratings based on fantasy points using different rating models.

---

## Table of Contents

- [Initialization](#initialization)  
- [Methods](#methods)  
  - [`_load_key() -> dict`](#_load_key---dict)  
  - [`_load() -> pd.DataFrame`](#_load---pddataframe)  
  - [`_partition() -> dict`](#_partition---dict)  
  - [`_filter_df(df: pd.DataFrame) -> pd.DataFrame`](#_filter_dfdf-pddataframe---pddataframe)  
  - [`_create_ratings(df: pd.DataFrame, model_type: str) -> pd.DataFrame`](#_create_ratingsdf-pddataframe-model_type-str---pddataframe)
  - [`run() -> None`](#run---None)  
- [Example Usage](#example-usage)  

---

## Initialization

```python
Statistics(seasons: list[int], ratings: list[str] = None)
```

### Parameters:
- `seasons` (`list[int]`): List of NFL seasons (years) to import data for (e.g., `[2023, 2024]`).
- `ratings` (`list[int]`, optional): List of regression model types to use for creating player ratings (e.g., `["ridge", "lasso"]`). Defaults to a predefined list if not provided.

### Raises:
- `Exception`: Logs errors and re-raises exceptions if data loading fails.

### Notes on Ratings:
- The class uses the provided list of rating models (strings) to generate player ratings for each position.
- This enables generating multiple ratings (e.g., Ridge, Lasso) from the same data in one run.

---

## Methods

### `_load_key() -> dict`

Loads seasonal rosters using `nfl.import_seasonal_rosters()` and builds a dictionary mapping `player_id` to a tuple of `(player_name, depth_chart_position)`.

#### Returns:
- `dict`: Mapping from `player_id` to `(player_name, depth_chart_position)`.

#### Logs:
- Errors encountered during data loading.

---

### `_load() -> pd.DataFrame`

Loads seasonal player data from [`nfl.import_seasonal_data()`](./import_seasonal_data.md).

- Drops the `season` and `season_type` columns.
- Groups by `player_id`, takes the mean of numeric columns.
- Drops rows with missing data.

#### Returns:
- `pd.DataFrame`: Aggregated seasonal data per player.

#### Logs:
- Errors encountered during data loading.

---

### `_partition() -> dict`

Partitions the loaded seasonal data into position-specific DataFrames indexed by `player_name`.

- Columns include `player_name` followed by all other statistics columns.
- Filters players by positions: `'QB'`, `'RB'`, `'WR'`, `'TE'`.
- Logs errors for players that cannot be processed.

#### Returns:
- `dict`: Keys are positions (`'QB'`, `'RB'`, `'WR'`, `'TE'`), values are DataFrames with player stats indexed by `player_name`.

#### Logs:
- Errors encountered during partitioning or player processing.

---

### `_filter_df(df: pd.DataFrame) -> pd.DataFrame`

Filters out columns where more than 10% of values are zero.

#### Parameters:
- `df` (`pd.DataFrame`): DataFrame to filter.

#### Returns:
- `pd.DataFrame`: Filtered DataFrame with columns having >10% non-zero values.

#### Logs:
- Errors encountered during filtering.

---

### `_create_ratings(df: pd.DataFrame, model_type: str) -> pd.DataFrame`

Creates player ratings using regression:

- Target variable `y` is `"fantasy_points_ppr"`.
- Features `X` exclude `"fantasy_points"` and `"fantasy_points_ppr"` columns.
- Uses the `Regression` class from `.regression` module.
- Supports specifying the regression model type

#### Parameters:
- `df` (`pd.DataFrame`): DataFrame to create ratings from.
- `model_type` (`str`, optional): Type of regression model to use (default `"ridge"`).

#### Returns:
- `pd.DataFrame`: Ratings computed by regression.

#### Logs:
- Errors encountered during ratings creation.

---

### `run() -> None`

Generates ratings for each position by:

- Partitioning the data into position-specific DataFrames.
- Filtering columns with `_filter_df`.
- Creating ratings with `_create_ratings`.
- Logs errors per position without stopping the process.

---

## Example Usage

```python
from source.statistics.statistics import Statistics
from source.database.excel import Excel

stats = Statistics([2024])
excel = Excel("output_file.xlsm")
excel.output_dfs(stats.run(), "output_sheet")
excel.close()