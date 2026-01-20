# FastAPI Endpoints

The [`api.py`](../backend/api.py) module provides REST API endpoints for accessing player rankings and detailed statistics. The API uses FastAPI and runs on `http://localhost:8000`.

---

## Table of Contents

- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [GET /](#get--status)
  - [GET /api/rankings](#get-apirankings)
  - [GET /api/player/{player_name}](#get-apiplayer{player_name})
  - [GET /api/search](#get-apisearch)
- [Response Models](#response-models)
- [Error Handling](#error-handling)

---

## Base URL

```
http://localhost:8000
```

## CORS

All endpoints have CORS enabled for frontend integration. In production, restrict `allow_origins` to your frontend domain.

---

## Endpoints

### GET / (Status)

Returns the API status and version information.

#### Response:
```json
{
  "status": "online",
  "message": "Fantasy Football Analysis API",
  "version": "0.1.0"
}
```

---

### GET /api/rankings

Get player rankings with both redraft and dynasty ratings and comprehensive percentile calculations.

#### Query Parameters:
- `format` (string, optional): `"redraft"` or `"dynasty"` (default: `"redraft"`) - retained for backward compatibility but all calculations are performed simultaneously
- `position` (string, optional): `"QB"`, `"RB"`, `"WR"`, `"TE"`, or `null` for all positions

#### Response (RankingsResponse):
```json
{
  "format": "redraft",
  "position": "WR",
  "model": "ridge",
  "rankings": {
    "WR": [
      {
        "name": "Ja'Marr Chase",
        "Rating": 401.52,
        "DynastyRating": 425.18,
        "Age": 24,
        "pos_percentile_redraft": 98.5,
        "pos_percentile_dynasty": 99.0,
        "overall_percentile_redraft": 95.2,
        "overall_percentile_dynasty": 96.1,
        "Rec": 127,
        "Rec Yds": 1456,
        ...
      },
      {
        "name": "Justin Jefferson",
        "Rating": 314.54,
        "DynastyRating": 330.27,
        "Age": 25,
        "pos_percentile_redraft": 92.3,
        "pos_percentile_dynasty": 93.8,
        "overall_percentile_redraft": 88.1,
        "overall_percentile_dynasty": 89.5,
        ...
      }
    ]
  }
}
```

#### Query Examples:

Get overall redraft rankings:
```
GET /api/rankings
```

Get QB rankings for dynasty format:
```
GET /api/rankings?format=dynasty&position=QB
```

#### Notes:
- **Rating**: Base rating calculated from Ridge Regression on historical performance
- **DynastyRating**: Base rating multiplied by age-based positional multiplier
  - Young players (below peak age): Boost for upside potential (e.g., RBs < 24)
  - Peak age players: Multiplier of 1.0 (no adjustment)
  - Veterans past prime: Declining multiplier based on position-specific curves
- **Age**: Player age from most recent season roster; defaults to position peak age if unavailable
- **Percentiles**: Four percentile calculations for comprehensive player evaluation
  - `pos_percentile_redraft`: Redraft ranking within position (0-100)
  - `pos_percentile_dynasty`: Dynasty ranking within position (0-100)
  - `overall_percentile_redraft`: Redraft ranking across all positions (0-100)
  - `overall_percentile_dynasty`: Dynasty ranking across all positions (0-100)
- **Eligible Players**: Only active players from the latest season are included (excludes retired/inactive)
- **Age Multiplier Curves by Position**:
  - QB: Peak 28, moderate decline (5%/year)
  - RB: Peak 24, steep decline (15%/year) - shortest career window
  - WR: Peak 26, moderate decline (8%/year)
  - TE: Peak 27, moderate decline (7%/year)

#### Status Codes:
- `200`: Success
- `400`: Invalid format or position
- `503`: Statistics data not loaded

---

### GET /api/player/{player_name}

Get detailed player information including statistics and team.

#### Path Parameters:
- `player_name` (string): Player's full name (e.g., `"Ja'Marr Chase"`)

#### Query Parameters:
- `season` (integer, optional): Specific season year (e.g., `2024`). If not provided, returns career-averaged stats.

#### Response (PlayerResponse):
```json
{
  "name": "Ja'Marr Chase",
  "position": "WR",
  "team": "CIN",
  "stats": {
    "Rating": 401.52,
    "Rec": 127,
    "Rec Yds": 1456,
    "Rec TD": 9,
    "Tgt": 143,
    "Rec YAC": 678,
    "PPR Pts": 165.8,
    "WOPR": 0.28,
    "Dakota": 0.45,
    ...
  },
  "available_seasons": [2021, 2022, 2023, 2024]
}
```

#### Query Examples:

Get career-averaged stats with rating:
```
GET /api/player/Ja'Marr%20Chase
```

Get 2024 season stats (with career-averaged rating):
```
GET /api/player/Ja'Marr%20Chase?season=2024
```

#### Notes:
- **Stats Filtering**: Zero-value or near-zero stats are filtered out for readability
- **Integer Conversion**: Stats like yards, TDs, and carries are displayed as integers
- **Available Seasons**: Only returned when viewing career-averaged data
- **Rating**: Remains the career-averaged rating even when viewing seasonal data
- **Display Names**: Column names are converted from internal names (e.g., `passing_yards` → `Pass Yds`)

#### Status Codes:
- `200`: Success
- `404`: Player not found
- `500`: Server error

---

### GET /api/search

Search for players by name.

#### Query Parameters:
- `q` (string, required): Search query (minimum 2 characters). Case-insensitive partial match.
- `position` (string, optional): Filter results by position (`"QB"`, `"RB"`, `"WR"`, `"TE"`)

#### Response (SearchResponse):
```json
{
  "query": "chase",
  "results": [
    {
      "name": "Ja'Marr Chase",
      "position": "WR",
      "rating": 401.52
    },
    {
      "name": "JK Dobbins",
      "position": "RB",
      "rating": 250.0
    }
  ],
  "count": 2
}
```

#### Query Examples:

Search for all players with "chase" in their name:
```
GET /api/search?q=chase
```

Search for wide receivers with "hill" in their name:
```
GET /api/search?q=hill&position=WR
```

#### Notes:
- **Partial Matching**: Matches anywhere in the player name (case-insensitive)
- **Sorting**: Results sorted by rating (highest first)
- **Limit**: Returns maximum 20 results
- **Active Players Only**: Searches across all active players in the system

#### Status Codes:
- `200`: Success
- `400`: Query too short (minimum 2 characters)
- `500`: Server error

---

## Response Models

### RankingsResponse

```python
{
    "format": str,              # "redraft" or "dynasty"
    "position": Optional[str],  # Position filter applied
    "model": str,               # "ridge"
    "rankings": Dict[str, List[Dict]]  # Position → List of player data
}
```

### PlayerResponse

```python
{
    "name": str,                    # Player name
    "position": str,                # Position (QB, RB, WR, TE)
    "team": Optional[str],          # Team abbreviation
    "stats": Dict[str, Any],        # Statistics dictionary
    "available_seasons": List[int]  # Seasons with data (if career-averaged)
}
```

### SearchResponse

```python
{
    "query": str,                       # Original search query
    "results": List[PlayerSearchResult], # List of matching players
    "count": int                        # Number of results
}
```

### PlayerSearchResult

```python
{
    "name": str,     # Player name
    "position": str, # Position (QB, RB, WR, TE)
    "rating": float  # Player rating
}
```

---

## Error Handling

All errors return JSON with the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios:

**Invalid Format:**
```json
{
  "detail": "Invalid format. Must be one of: redraft, dynasty"
}
```

**Invalid Position:**
```json
{
  "detail": "Invalid position. Must be one of: QB, RB, WR, TE"
}
```

**Player Not Found:**
```json
{
  "detail": "Player 'Nonexistent Player' not found"
}
```

**Search Query Too Short:**
```json
{
  "detail": "Search query must be at least 2 characters"
}
```

---

## Data Sources

- **Player Ratings**: Averaged across specified seasons using Ridge Regression model
- **Depth Charts**: Real-time data from ESPN (refreshed on app startup)
- **Schedules**: NFL official schedule data (includes current season)
- **Statistics**: Historical NFL player statistics from `nfl_data_py` API

---

## Example Usage

### Python (with requests library):

```python
import requests

# Get redraft WR rankings
response = requests.get("http://localhost:8000/api/rankings", 
                       params={"format": "redraft", "position": "WR"})
rankings = response.json()

# Get player details
response = requests.get("http://localhost:8000/api/player/Ja'Marr Chase")
player = response.json()

# Search for players
response = requests.get("http://localhost:8000/api/search",
                       params={"q": "mahomes", "position": "QB"})
results = response.json()
```

### JavaScript (with fetch):

```javascript
// Get rankings
const rankings = await fetch("/api/rankings?format=redraft&position=WR")
  .then(r => r.json());

// Get player
const player = await fetch("/api/player/Ja'Marr Chase")
  .then(r => r.json());

// Search
const results = await fetch("/api/search?q=mahomes&position=QB")
  .then(r => r.json());
```
