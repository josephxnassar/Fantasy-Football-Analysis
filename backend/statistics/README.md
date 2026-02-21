# Statistics Module

Last verified: 2026-02-15

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates season/week stat caches and player metadata consumed by API routes.

## Table of Contents

1. [Primary Entry](#primary-entry)
2. [Data Inputs](#data-inputs)
3. [Processing Pipeline](#processing-pipeline)
4. [Output Cache Shape](#output-cache-shape)
5. [Related Files](#related-files)
6. [Rebuild Command](#rebuild-command)

## Primary Entry

- Main class: [`statistics.py`](statistics.py)
- Core method: `Statistics.run()`

## Data Inputs

Loaded from `nflreadpy`:

| Dataset | Loader |
|---|---|
| Rosters | `nfl.load_rosters` |
| Player stats | `nfl.load_player_stats` |
| Snap counts | `nfl.load_snap_counts` |

Configured seasons:
- [`backend/util/constants.py`](../util/constants.py) -> `SEASONS`

## Processing Pipeline

1. Extract roster metadata in one pass:
- age
- current eligibility
- team
- headshot URL
- rookie flag

2. Filter to regular season fantasy positions (`QB/RB/WR/TE`), then aggregate per player/season.

3. Rename columns via `COLUMN_NAME_MAP` and append derived stats (`Yds/Rec`, `Yds/Rush`).

4. Build season and weekly views:
- `by_year` (season -> position -> DataFrame)
- `player_weekly_stats` (player -> week records with snap share)

5. Build searchable player metadata from roster fields:
- `name`
- `position`
- `team`
- `age`
- `headshot_url`
- `is_rookie`
- `is_eligible`

## Output Cache Shape

Public keys used by API routes:
- `all_players`
- `by_year`
- `player_weekly_stats`

## Related Files

- Helpers: [`util/stats_helpers.py`](util/stats_helpers.py)
- Constants/config: [`../util/constants.py`](../util/constants.py)

## Rebuild Command

```bash
uv run python backend/refresh_data.py
```
