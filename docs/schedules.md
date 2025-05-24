
# Schedules Class

The [`Schedules`](../source/schedules.py) class provides functionality for importing and organizing NFL schedule data for given seasons. It extracts regular season matchups and partitions them by team, filling in bye weeks as needed.

---

## Table of Contents

- [Initialization](#initialization)  
- [Methods](#methods)  
  - [`_load_data() -> pd.DataFrame`](#_load_data---pddataframe)  
  - [`_split_schedules_by_team() -> dict[str, pd.DataFrame]`](#_split_schedules_by_team---dictstr-pddataframe)  
  - [`_fill_bye_weeks(df: pd.DataFrame, team: str) -> pd.DataFrame`](#_fill_bye_weeksdf-pddataframe-team-str---pddataframe)  
  - [`run() -> None`](#run---None)  
- [Example Usage](#example-usage)

---

## Initialization

```python
Schedules(seasons: list[int])
```

### Parameters:
- `seasons` (`list[int]`): List of years to import schedules for (e.g., `[2023, 2024]`).

### Raises:
- `Exception`: If the API call fails when retrieving schedules, an error is logged and the exception is raised.

---

## Methods

### `_load_data() -> pd.DataFrame`

Fetches NFL regular season schedules for the specified seasons using `import_schedules()` from the `nfl_data_py` API. Filters the data to only include regular season games (`game_type == 'REG'`), returning the columns `week`, `away_team`, and `home_team`.

#### Returns:
- `pd.DataFrame`: DataFrame of filtered regular season schedules.

#### Raises:
- `Exception`: If the data loading fails, the error is logged and the exception is raised.

---

### `_split_schedules_by_team() -> dict[str, pd.DataFrame]`

Creates a dictionary mapping each team abbreviation to their schedule DataFrame.

- Home and away games are combined, with columns renamed to `Team` and `Opponent` accordingly.
- Each team's schedule is indexed by week and sorted.
- Errors for individual teams during processing are logged but do not stop the entire operation.

#### Returns:
- `dict[str, pd.DataFrame]`: Mapping from team abbreviation to their weekly opponent schedule.

#### Raises:
- `Exception`: If the splitting process fails, the error is logged and the exception is raised.

---

### `_fill_bye_weeks(df: pd.DataFrame, team: str) -> pd.DataFrame`

Fills missing weeks in a team's schedule DataFrame with "BYE" to represent bye weeks.

#### Parameters:
- `df` (`pd.DataFrame`): The team's schedule indexed by week.
- `team` (`str`): Team abbreviation (used for the index name).

#### Returns:
- `pd.DataFrame`: Team schedule with all weeks from 1 to the total number of weeks, inserting "BYE" for missing weeks.

#### Raises:
- `Exception`: If filling bye weeks fails, logs the error and raises the exception.

---

### `run() -> None`

Generates the complete schedules for each team including bye weeks by combining the splitting and filling steps.

---

## Example Usage

```python
from source import Schedules
from source.database import Excel

schedule = Schedules([2024])
team_schedules = schedule.run()

excel = Excel("output_file.xlsm")
excel.output_dfs(team_schedules, "output_sheet")
excel.close()
```

---