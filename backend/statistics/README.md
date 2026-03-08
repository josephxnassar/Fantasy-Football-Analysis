# Statistics Module

Last verified: 2026-03-07

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates statistics caches consumed by the API (`all_players`, `by_year`, `player_weekly_stats`).

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
| Player stats (weekly) | `nfl.load_player_stats(summary_level="week")` |
| Player stats (seasonal reg) | `nfl.load_player_stats(summary_level="reg")` |
| Fantasy opportunity (weekly) | `nfl.load_ff_opportunity(stat_type="weekly")` |
| Next Gen passing/receiving/rushing | `nfl.load_nextgen_stats(...)` |
| PFR advanced weekly pass/rush/rec | `nfl.load_pfr_advstats(..., summary_level="week")` |
| PFR advanced seasonal pass/rush/rec | `nfl.load_pfr_advstats(..., summary_level="season")` |
| Snap counts | `nfl.load_snap_counts` |

Season guards used in loaders:
- PFR advanced: `>= 2018`
- Snap counts: `>= 2012`

Configured seasons:
- [`backend/util/constants.py`](../util/constants.py) -> `SEASONS`

## Processing Pipeline

1. Load all stat sources in parallel (`_load_statistics_sources`) and rosters in parallel with source loading (`run`).
2. Normalize team abbreviations in each source loader (for example `LA -> LAR`, `WAS -> WSH`) before downstream joins, then apply regular-season + fantasy-position filtering where applicable (`QB/RB/WR/TE`) and keep mapped columns.
3. Merge all weekly sources onto base weekly player stats.
4. Normalize PFR seasonal player names (`align_pfr_seasonal_names`) then merge onto base seasonal player stats.
5. Add derived metrics (`Yds/Rec`, `Yds/Rush`), combine stat aliases into canonical keys, roll selected weekly-only metrics up into seasonal player rows (`WEEKLY_SUM_AGGREGATE_METRICS` via sum, `WEEKLY_AVERAGED_AGGREGATE_METRICS` via plain mean), and compute positional ranks.
6. Collect represented player names from shaped DataFrames (`_collect_stats_player_names`).
7. Build final cache views in parallel (`_build_statistics_data`):
- Seasonal (`_build_seasonal_player_stats`): season -> position -> DataFrame.
- Weekly (`_build_weekly_player_stats`): player -> list of weekly records.
- Filtered player metadata (`_build_all_players`): `all_players`.
- Seasonal and weekly views are cleaned for JSON safety (`NaN/inf` handling) during build.

## Output Cache Shape

Public keys used by API routes:
- `all_players`
- `by_year`
- `player_weekly_stats`

Notes:
- `all_players` is stats-backed (not full raw roster list).

## Related Files

- Orchestration + cache-shape builders: [`statistics.py`](statistics.py)
- Reusable dataframe helpers: [`util/stats_helpers.py`](util/stats_helpers.py)
- Constants/config: [`../util/constants.py`](../util/constants.py)

## Rebuild Command

```bash
uv run python backend/refresh_data.py
```
