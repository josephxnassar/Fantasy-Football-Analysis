# `ESPNDepthChart` Class

The [`ESPNDepthChart`](../backend/depth_chart/espn.py) class scrapes up-to-date team depth charts from ESPN's website. It supports generating team-by-team rosters and their depth chart order for relevant offensive positions (QB, RB, WR, TE).

---

## Table of Contents

- [Initialization](#initialization)
- [Methods](#methods)
  - [`_get_soup(team: str) -> BeautifulSoup`](#_get_soupteam-str---beautifulsoup)
  - [`_parse_soup(soup: BeautifulSoup) -> tuple`](#_parse_soupsoup-beautifulsoup---tuple)
  - [`_create_depth_chart(positions: list, players: list) -> pd.DataFrame`](#_create_depth_chartpositions-list-players-list---pddataframe)
  - [`run() -> None`](#run---None)
- [Cache Structure](#cache-structure)
- [Example Usage](#example-usage)

---

## Initialization

```python
ESPNDepthChart()
```

### Notes:
- Always uses 2025 as the season (for current depth charts)
- Automatically sets `teams` attribute from `constants.TEAMS` (all 32 NFL teams)
- No parameters required

---

## Methods

### `_get_soup(team: str) -> BeautifulSoup`

Sends an HTTP GET request to the ESPN depth chart page for a given team and returns a BeautifulSoup object of the parsed HTML.

#### Parameters:
- `team` (`str`): Team abbreviation (e.g., `"DAL"` for the Dallas Cowboys, `"KC"` for Kansas City Chiefs).

#### URL Format:
```
https://www.espn.com/nfl/team/depth/_/name/{team}
```

#### Returns:
- `BeautifulSoup`: Parsed HTML soup object ready for extraction.

#### Logs:
- Errors if HTTP request fails (includes team name in log).

#### Raises:
- `Exception`: Logged and re-raised if the request fails.

---

### `_parse_soup(soup: BeautifulSoup) -> tuple`

Parses the ESPN depth chart HTML to extract positions and player names.

#### Parameters:
- `soup` (`BeautifulSoup`): Parsed HTML from ESPN depth chart page.

#### Process:
- Finds the first table (contains position headers: QB, RB, WR, TE, etc.)
- Finds the second table (contains player names in depth order)
- Extracts all position headers
- Extracts all player names from tbody rows

#### Returns:
- `tuple`: `(positions_list, players_list)`
  - `positions_list` (`list[str]`): Position abbreviations (e.g., `['QB', 'RB', 'WR', 'TE']`)
  - `players_list` (`list[str]`): Flattened list of player names in depth order

#### Logs:
- Errors encountered during parsing.

#### Raises:
- `Exception`: Logged and re-raised if parsing fails.

---

### `_create_depth_chart(positions: list, players: list) -> pd.DataFrame`

Organizes the scraped position and player data into a structured DataFrame.

#### Parameters:
- `positions` (`list[str]`): List of player positions extracted from ESPN (e.g., `['QB', 'RB', 'WR', 'TE']`).
- `players` (`list[str]`): Flattened list of player names in depth order.

#### Process:
1. For each position in `constants.POSITIONS` (QB, RB, WR, TE):
   - Takes 4 consecutive players from the flattened list (Starter, 2nd, 3rd, 4th string)
2. Creates DataFrame with columns: `[Starter, 2nd, 3rd, 4th]`
3. Index is the position
4. Removes suffix indicators like "Q", "D", "O", "IR", "PUP", "NFI", "SUS" from player names

#### Returns:
- `pd.DataFrame`: Depth chart indexed by position with columns for each depth level.

#### Example Output:
```
Position  Starter          2nd              3rd              4th
QB        Patrick Mahomes  Isiah Pacheco    Skyy Moore       ...
RB        Isiah Pacheco    Jerick McKinnon  ...
WR        Travis Kelce     ...
TE        ...
```

#### Logs:
- Errors encountered during depth chart creation.

#### Raises:
- `Exception`: Logged and re-raised if creation fails.

---

### `run() -> None`

Main execution method that constructs depth charts for all NFL teams.

#### Process:
1. Iterates through all 32 teams in `constants.TEAMS`
2. For each team:
   - Fetches and parses the ESPN page
   - Extracts positions and players
   - Creates depth chart DataFrame
   - Stores in cache with team name as key
3. Handles errors per team without stopping execution

#### Cache Structure:
- Keys: Team abbreviations (e.g., 'KC', 'PHI', 'DAL')
- Values: DataFrames with depth chart data

#### Logs:
- Errors per team without stopping overall execution.

---

## Cache Structure

After calling `run()`, the cache contains:

```python
{
    'KC': DataFrame,   # Kansas City Chiefs depth chart
    'PHI': DataFrame,  # Philadelphia Eagles depth chart
    'DAL': DataFrame,  # Dallas Cowboys depth chart
    ...                # All 32 NFL teams
}
```

Each DataFrame:
- Index: Offensive positions (QB, RB, WR, TE)
- Columns: `[Starter, 2nd, 3rd, 4th]` (depth chart order)
- Values: Player names

---

## Example Usage

```python
from backend.depth_chart import ESPNDepthChart
from backend.database.service import SQLService

# Create instance and run
depth_chart = ESPNDepthChart()

# Access cache data
all_charts = depth_chart.get_cache()  # Dict[str, DataFrame]
kc_depth = all_charts['KC']           # Chiefs depth chart
mahomes = kc_depth.loc['QB', 'Starter']  # Patrick Mahomes

# Save to database
db_service = SQLService()
db_service.save_to_db(depth_chart.get_cache(), "ESPNDepthChart")
db_service.close()
```

---

## Notes

- **Real-time Data**: Fetches current depth charts directly from ESPN (not cached in code)
- **Web Scraping**: Uses BeautifulSoup to parse HTML tables
- **User Agent**: Includes standard browser user-agent to avoid blocks
- **Error Resilience**: Logs errors per team but continues with others
- **Suffix Removal**: Automatically strips status indicators (IR, PUP, etc.) from player names
