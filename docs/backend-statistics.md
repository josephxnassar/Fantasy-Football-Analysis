# `Statistics` Class

The [`Statistics`](../backend/statistics/statistics.py) class provides functionality for importing, processing, and analyzing NFL seasonal data. It performs key operations such as loading player data, computing averaged stats across seasons, partitioning by player positions, filtering statistics columns, and creating player ratings based on fantasy points using Ridge Regression.

---

## Table of Contents

- [Initialization](#initialization)  
- [Attributes](#attributes)
- [Methods](#methods)  
  - [`_load_key() -> dict`](#_load_key---dict)  
  - [`_load() -> pd.DataFrame`](#_load---pddataframe)
  - [`_compute_averaged_data() -> pd.DataFrame`](#_compute_averaged_data---pddataframe)
  - [`_split_by_year() -> dict`](#_split_by_year---dict)
  - [`_partition_data(data: pd.DataFrame) -> dict`](#_partition_datadata-pddataframe---dict)  
  - [`_filter_df(df: pd.DataFrame) -> pd.DataFrame`](#_filter_dfdf-pddataframe---pddataframe)
  - [`_rename_columns(df: pd.DataFrame) -> pd.DataFrame`](#_rename_columnsdf-pddataframe---pddataframe)  
  - [`_create_ratings(df: pd.DataFrame, method: str) -> pd.DataFrame`](#_create_ratingsdf-pddataframe-method-str---pddataframe)
  - [`run() -> None`](#run---None)  
- [Cache Structure](#cache-structure)
- [Example Usage](#example-usage)  

---

## Initialization

```python
Statistics(seasons: list[int], method: str = "ridge")
```

### Parameters:
- `seasons` (`list[int]`): List of NFL seasons (years) to import data for (e.g., `[2023, 2024]`).
- `method` (`str`, optional): Regression model type for creating ratings. Currently supports `"ridge"`. Defaults to `"ridge"`.

### Raises:
- `Exception`: Logs errors and re-raises exceptions if data loading fails.

### Initialization Flow:
1. Loads seasonal rosters and player metadata via `_load_key()`
2. Loads raw seasonal data via `_load()`
3. Computes career-averaged statistics via `_compute_averaged_data()`
4. Splits raw data by season via `_split_by_year()`

---

## Attributes

After initialization, the following attributes are available:

- `id_to_player` (`Dict[str, Tuple[str, str]]`): Mapping from `player_id` to `(player_name, position)`.
- `raw_seasonal_data` (`pd.DataFrame`): Complete raw seasonal data (all seasons combined).
- `seasonal_data` (`pd.DataFrame`): Career-averaged statistics (aggregated across all seasons).
- `seasonal_data_by_year` (`Dict[int, pd.DataFrame]`): Raw data split by individual season.
- `player_ages` (`Dict[str, int]`): Player names mapped to their ages (used for dynasty format).
- `eligible_players` (`Set[str]`): Active players from the latest season (excludes retired/inactive).

---

## Methods

### `_load_key() -> dict`

Loads seasonal rosters using `nfl.import_seasonal_rosters()` and builds a dictionary mapping `player_id` to a tuple of `(player_name, depth_chart_position)`. Also extracts player ages for dynasty rating calculations and identifies eligible (active) players.

#### Returns:
- `dict`: Mapping from `player_id` to `(player_name, depth_chart_position)`.

#### Side Effects:
- Sets `self.player_ages`: Dictionary mapping player names to their ages.
- Sets `self.eligible_players`: Set of active players from the latest season.

#### Logs:
- Success: Number of players with loaded ages.
- Errors: Any issues encountered during roster loading.

---

### `_load() -> pd.DataFrame`

Loads raw seasonal player data from `nfl.import_seasonal_data()` for all specified seasons. This is the abstract method implementation from `BaseSource`.

#### Returns:
- `pd.DataFrame`: Complete raw seasonal data with columns like `player_id`, `season`, `season_type`, and statistics.

#### Logs:
- Errors encountered during data loading.

---

### `_compute_averaged_data() -> pd.DataFrame`

Computes career-averaged statistics by aggregating raw seasonal data across all seasons for each player.

#### Process:
- Drops `season` and `season_type` columns
- Groups by `player_id`
- Takes the mean of numeric columns
- Drops rows with missing data

#### Returns:
- `pd.DataFrame`: Averaged statistics per player (one row per player).

#### Logs:
- Errors encountered during computation.

---

### `_split_by_year() -> dict`

Splits raw seasonal data into separate DataFrames, one per season.

#### Returns:
- `dict`: Keys are season years (int), values are DataFrames with that season's data.

#### Logs:
- Errors encountered during splitting.

---

### `_partition_data(data: pd.DataFrame) -> dict`

Partitions a given DataFrame (can be averaged or seasonal data) into position-specific DataFrames indexed by `player_name`.

#### Parameters:
- `data` (`pd.DataFrame`): DataFrame containing `player_id` and statistics columns.

#### Process:
- Maps each `player_id` to player name and position using `id_to_player`
- Filters players by valid positions: `'QB'`, `'RB'`, `'WR'`, `'TE'`
- Creates separate DataFrames for each position with `player_name` as index

#### Returns:
- `dict`: Keys are positions (`'QB'`, `'RB'`, `'WR'`, `'TE'`), values are DataFrames with player stats indexed by `player_name`.

#### Logs:
- Errors for individual players that cannot be processed.

---

### `_filter_df(df: pd.DataFrame) -> pd.DataFrame`

Filters out columns where more than 10% of values are zero (sparse data).

#### Parameters:
- `df` (`pd.DataFrame`): DataFrame to filter.

#### Returns:
- `pd.DataFrame`: Filtered DataFrame with only meaningful statistics columns (>90% non-zero values).

#### Logs:
- Errors encountered during filtering.

---

### `_rename_columns(df: pd.DataFrame) -> pd.DataFrame`

Renames columns to presentable display names using the mapping in `constants.COLUMN_NAME_MAP`.

#### Parameters:
- `df` (`pd.DataFrame`): DataFrame with internal column names (e.g., `passing_yards`, `receiving_tds`).

#### Returns:
- `pd.DataFrame`: DataFrame with friendly display names (e.g., `Pass Yds`, `Rec TD`).

#### Example Mappings:
- `passing_yards` → `Pass Yds`
- `receiving_tds` → `Rec TD`
- `fantasy_points_ppr` → `PPR Pts`

#### Logs:
- Errors encountered during renaming.

---

### `_create_ratings(df: pd.DataFrame, method: str) -> pd.DataFrame`

Creates player ratings using Ridge Regression.

#### Parameters:
- `df` (`pd.DataFrame`): DataFrame with player statistics (must include `fantasy_points_ppr` target).
- `method` (`str`): Regression model type (currently only `"ridge"` supported).

#### Process:
1. Target variable `y` = `"fantasy_points_ppr"`
2. Features `X` = all columns except `"fantasy_points"` and `"fantasy_points_ppr"`
3. Uses `Regression` class from `.ratings.regression` module
4. Fits model and generates ratings

#### Returns:
- `pd.DataFrame`: DataFrame with added `rating` column, sorted descending by rating.

#### Logs:
- Errors encountered during model fitting or rating generation.

---

### `run() -> None`

Main execution method that generates ratings for each position and stores results in cache.

#### Process:
1. **Process Averaged Data:**
   - Partitions career-averaged data by position
   - Filters sparse columns
   - Generates ratings for each position
   - Renames columns to display names

2. **Process Seasonal Data:**
   - Partitions individual season data by position
   - Filters sparse columns
   - Renames columns (no ratings for seasonal data)

3. **Store Cache:**
   - Saves nested structure with `averaged`, `by_year`, metadata, etc.

#### Cache Structure:
- `averaged`: Position → DataFrame with ratings
- `by_year`: Season → (Position → DataFrame)
- `available_seasons`: List of season years
- `eligible_players`: Set of active player names
- `player_ages`: Dictionary of player name → age

#### Logs:
- Errors per position without stopping overall execution.

---

## Cache Structure

After calling `run()`, the cache contains:

```python
{
    'averaged': {
        'QB': DataFrame,  # Averaged stats with ratings
        'RB': DataFrame,
        'WR': DataFrame,
        'TE': DataFrame
    },
    'by_year': {
        2024: {
            'QB': DataFrame,  # 2024 season stats (no ratings)
            'RB': DataFrame,
            ...
        },
        2023: {...},
        ...
    },
    'available_seasons': [2016, 2017, ..., 2024],
    'eligible_players': {'Player Name 1', 'Player Name 2', ...},
    'player_ages': {'Player Name 1': 26, 'Player Name 2': 28, ...}
}
```

---

## Example Usage

```python
from backend.statistics import Statistics
from backend.database.service import SQLService

# Create instance and run
stats = Statistics([2023, 2024])

# Access cache data
averaged_ratings = stats.get_cache()['averaged']  # Career-averaged with ratings
seasonal_data = stats.get_cache()['by_year']      # Individual season stats

# Save to database
db_service = SQLService()
db_service.save_to_db(stats.get_cache(), "Statistics")
db_service.close()
```
