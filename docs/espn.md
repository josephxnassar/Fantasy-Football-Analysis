# `ESPNDepthChart` Class

The [`ESPNDepthChart`](../source/depth_chart/espn.py) class scrapes *updated* team depth charts from ESPN's website. It supports generating team-by-team rosters and their depth chart order for relevant offensive positions.

---

## Table of Contents

- [Initialization](#initialization)
- [Methods](#methods)
  - [`_get_soup(team: str)`](#_get_soupteam-str)
  - [`_parse_soup(soup: BeautifulSoup) -> tuple`](#_parse_soupsoup-beautifulsoup---tuple)
  - [`_create_depth_chart(positions: list, players: list) -> pd.DataFrame`](#_create_depth_chartpositions-list-players-list---pddataframe)
  - [`run() -> dict`](#run---dict)
- [Example Usage](#example-usage)

---

## Initialization

```python
ESPNDepthChart()
```

### Attributes:
- `teams` (`list[str]`): List of NFL team abbreviations used to construct URLs for scraping ESPN.

---

## Methods

### `_get_soup(team: str)`

Sends an HTTP GET request to the ESPN depth chart page for a given team and returns a BeautifulSoup of the HTML.

#### Parameters:
- `team` (`str`): Team abbreviation (e.g., `"DAL"` for the Dallas Cowboys).

#### Returns:
- `BeautifulSoup`: Parsed HTML soup object.

#### Raises:
- Exits the program if an `HTTPError` is encountered.

---

### `_parse_soup(soup: BeautifulSoup) -> tuple`

Parses the two tables from the soup object to extract positions and players.

#### Parameters:
- `soup` (`BeautifulSoup`): Parsed HTML from the team depth chart page.

#### Returns:
- `tuple`: A tuple containing a list of positions and a list of player names.

---

### `_create_depth_chart(positions: list, players: list) -> pd.DataFrame`

Organizes the scraped position and player data into a structured DataFrame for positions of interest.

#### Parameters:
- `positions` (`list`): List of player positions.
- `players` (`list`): Flattened list of player names.

#### Returns:
- `pd.DataFrame`: A DataFrame indexed by position with columns for starter, 2nd, 3rd, and 4th string players.

---

### `run() -> dict`

Constructs depth charts for all NFL teams defined in `self.teams`.

---

## Example Usage

```python
from source.depth_chart.espn import ESPNDepthChart
from source.database import Excel

espn = ESPNDepthChart()
excel = Excel("output_file.xlsm")
excel.output_dfs(espn.run(), "output_sheet")
excel.close()
```

---