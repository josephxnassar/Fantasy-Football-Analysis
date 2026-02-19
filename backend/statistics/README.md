# Statistics Module

Last verified: 2026-02-15

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)
[![Ridge Regression](https://img.shields.io/badge/Model-Ridge-0EA5E9)](ratings/regression/regression.py)

Generates rating/rank metadata and season/week stat caches consumed by API routes.

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

5. Train per-position Ridge models to produce base ratings.

6. Derive rating variants:
- `redraft_rating` via position multipliers
- `dynasty_rating` via age multipliers

7. Compute rank metadata:
- `overall_rank_redraft`
- `overall_rank_dynasty`
- `pos_rank_redraft`
- `pos_rank_dynasty`

## Output Cache Shape

Public keys used by API routes:
- `all_players`
- `by_year`
- `player_weekly_stats`

Canonical rating fields:
- `redraft_rating`
- `dynasty_rating`

## Related Files

- Helpers: [`util/stats_helpers.py`](util/stats_helpers.py)
- Model interface: [`ratings/base_ratings.py`](ratings/base_ratings.py)
- Ridge model: [`ratings/regression/regression.py`](ratings/regression/regression.py)
- Constants/config: [`../util/constants.py`](../util/constants.py)

## Rebuild Command

```bash
uv run python backend/refresh_data.py
```
