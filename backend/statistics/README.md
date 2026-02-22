# Statistics Module

Last verified: 2026-02-22

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates statistics caches consumed by the API (`all_players`, `by_year`, `player_weekly_stats`, `player_name_aliases`).

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
2. Normalize each source to regular season + fantasy positions (`QB/RB/WR/TE`) and keep mapped columns.
3. Merge all weekly sources onto base weekly player stats.
4. Merge seasonal PFR sources onto base seasonal player stats.
5. Add derived metrics (`Yds/Rec`, `Yds/Rush`) and interpreted metrics (canonical coalesced stats + percentiles + volume score).
6. Build final cache views:
- Seasonal (`build_seasonal_data`): season -> position -> DataFrame.
- Weekly (`build_weekly_player_stats`): player -> list of weekly records.
- Both views are cleaned for JSON safety (`NaN/inf` handling) during build.
7. Build player metadata from rosters (`build_all_players`) filtered to only players that exist in stats outputs.
8. Build alias map (`build_player_name_aliases`) so suffix variants resolve to one canonical stats name.

## Output Cache Shape

Public keys used by API routes:
- `all_players`
- `by_year`
- `player_weekly_stats`
- `player_name_aliases`

Notes:
- `all_players` is stats-backed (not full raw roster list).
- Alias normalization ignores suffix tokens from `constants.NAME_SUFFIXES`.

## Related Files

- Helpers: [`util/stats_helpers.py`](util/stats_helpers.py)
- Constants/config: [`../util/constants.py`](../util/constants.py)

## Rebuild Command

```bash
uv run python backend/refresh_data.py
```
