# Statistics Layer

Last verified: 03/20/2026

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates the statistics cache used by the backend: `all_players`, `seasonal_player_stats`, `weekly_player_stats`, and `meta`.

## Table of Contents

1. [Data Inputs](#data-inputs)
2. [Output Shape](#output-shape)
3. [Known Issues](#known-issues)
4. [Resolved](#resolved)

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

## Output Shape

**`all_players`**

shape: `(player_name, player_id) -> player_record`

```python
all_players[("Amon-Ra St. Brown", "00-0036963")] = {
    "name": "Amon-Ra St. Brown",
    "player_id": "00-0036963",
    "position": "WR",
    "age": 25,
    "team": "DET",
    "headshot_url": "...",
    "is_rookie": False,
    "is_eligible": True,
}
```

**`seasonal_player_stats`**

shape: `season -> position -> (player_name, player_id) -> seasonal_record`

```python
seasonal_player_stats[2024]["WR"][("Amon-Ra St. Brown", "00-0036963")] = {
    "rec_recs": 115,
    "rec_yds": 1263,
    "rec_tds": 12,
    "fantasy_fp_ppr": 313.3,
    "fantasy_fp_ppr_rank": 3,
    ...
}
```

**`weekly_player_stats`**

shape: `season -> position -> (player_name, player_id) -> [weekly_records]`

```python
weekly_player_stats[2024]["WR"][("Amon-Ra St. Brown", "00-0036963")] = [
    {
        "base_week": 1,
        "rec_recs": 6,
        "rec_yds": 95,
        "rec_tds": 1,
        "fantasy_fp_ppr": 21.5,
        "fantasy_fp_ppr_rank": 8,
        ...
    },
    ...
]
```

**`meta`**

shape: `{key: count}`

```python
meta = {
    "player_positions_count": 2660,
    "player_ages_count": 2252,
    "eligible_player_count": 966,
    "headshot_player_count": 2445,
    "player_teams_count": 971,
    "rookie_player_count": 237,
    "seasonal_record_count": 4764,
    "weekly_record_count": 45674,
}
```

## Known Issues

- Import sources can contain weeks where players did not record stats or were inactive.
- Player name mismatches can still happen across sources, especially around punctuation, suffixes, renamed players, new players not yet added to the alias map, and PFR/snap imports that do not expose `player_id`.

## Resolved

- Weekly PFR previously had `game_id` merge conflicts when base weekly rows had missing `game_id` values. This was resolved by removing `base_game_id` from weekly PFR joins.
- Seasonal PFR rushing and receiving previously had multi-role position conflicts. This was mostly resolved by removing `base_pos` from those joins.
- Seasonal PFR rushing and receiving previously had `2TM` / `3TM` team conflicts. This is handled by dropping `base_team` when team is not part of the join.
