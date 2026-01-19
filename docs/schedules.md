# `Schedules` Class

The [`Schedules`](../backend/schedules/schedules.py) class provides functionality for importing and organizing NFL schedule data for given seasons. It extracts regular season matchups and partitions them by team, filling in bye weeks as needed.

---

## Table of Contents

- [Initialization](#initialization)  
- [Methods](#methods)  
  - [`_load() -> pd.DataFrame`](#_load---pddataframe)  
  - [`_fill_bye_weeks(df: pd.DataFrame, team: str) -> pd.DataFrame`](#_fill_bye_weeksdf-pddataframe-team-str---pddataframe) 
  - [`_create_combined_schedule() -> pd.DataFrame`](#_create_combined_schedule---pddataframe)  
  - [`run() -> None`](#run---None)  
- [Cache Structure](#cache-structure)
- [Example Usage](#example-usage)

---

## Initialization

```python
Schedules(seasons: list[int])
```

### Parameters:
- `seasons` (`list[int]`): List of years to import schedules for (e.g., `[2023, 2024]`, or `[2025]` for current season).

### Raises:
- `Exception`: If the API call fails when retrieving schedules, an error is logged and the exception is raised.

---

## Methods

### `_load() -> pd.DataFrame`

Fetches NFL regular season schedules for the specified seasons using `import_schedules()` from the `nfl_data_py` API. Filters the data to only include regular season games (`game_type == 'REG'`), returning the columns `week`, `away_team`, and `home_team`.

Also handles team name standardization (e.g., "LA" → "LAR", "WAS" → "WSH").

#### Returns:
- `pd.DataFrame`: DataFrame of filtered regular season schedules with columns `[week, away_team, home_team]`.

#### Side Effects:
- Sets `self.weeks`: Total number of weeks in the season.

#### Logs:
- Errors encountered during data loading.

---

### `_fill_bye_weeks(df: pd.DataFrame, team: str) -> pd.DataFrame`

Fills missing weeks in a team's schedule DataFrame with "BYE" to represent bye weeks.

#### Parameters:
- `df` (`pd.DataFrame`): The team's schedule indexed by week (with column `Opponent`).
- `team` (`str`): Team abbreviation (used as the new index name).

#### Returns:
- `pd.DataFrame`: Team schedule with all weeks from 1 to `self.weeks`, inserting "BYE" for missing weeks. Index is renamed to the team abbreviation.

#### Logs:
- Errors encountered during bye week filling.

---

### `_create_combined_schedule() -> pd.DataFrame`

Creates a combined schedule DataFrame containing both home and away games for all teams.

#### Process:
- Splits `master_schedule` into home and away perspectives
- Renames columns to standardized format: `Team` and `Opponent`
- Home team with away opponent (as Opponent)
- Away team with home opponent (as Opponent)
- Concatenates both perspectives

#### Returns:
- `pd.DataFrame`: Combined schedules with columns `[week, Team, Opponent]`.

#### Logs:
- Errors encountered during schedule creation.

---

### `run() -> None`

Generates complete schedules for each team including bye weeks.

#### Process:
1. Creates combined schedule (both home and away games)
2. Groups by team
3. For each team:
   - Fills missing bye weeks using `_fill_bye_weeks`
   - Sets team name as index
4. Stores all team schedules in cache

#### Cache Structure:
- Keys: Team abbreviations (e.g., 'KC', 'PHI')
- Values: DataFrame with index=week, columns=['Opponent'], index_name=team_abbreviation

#### Logs:
- Errors per team without stopping overall execution.

---

## Cache Structure

After calling `run()`, the cache contains:

```python
{
    'KC': DataFrame,    # Index: weeks 1-17, Column: Opponent, Index name: 'KC'
    'PHI': DataFrame,
    'DAL': DataFrame,
    ...                 # All 32 NFL teams
}
```

Example DataFrame for a team:
```
      Opponent
KC           
1          OAK
2          LAC
3          BYE
4          BAL
...
```

---

## Example Usage

```python
from backend.schedules import Schedules
from backend.database.service import SQLService

# Create instance and run
schedules = Schedules([2025])

# Access cache data
team_schedules = schedules.get_cache()  # Dict[str, DataFrame]
kc_schedule = team_schedules['KC']      # Chiefs schedule

# Save to database
db_service = SQLService()
db_service.save_to_db(schedules.get_cache(), "Schedules")
db_service.close()
```
