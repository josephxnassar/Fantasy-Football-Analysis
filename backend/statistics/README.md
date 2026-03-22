# Statistics Layer

Last verified: 03/20/2026

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates the statistics cache used by the backend: `all_players`, `seasonal_player_stats`, `weekly_player_stats`, and `meta`.

## Known Issues

- Data serialization takes too long and doesn't work with NAN or INF.

### Merge Conflicts

- Weeks in which players are inactive do not create a record.
- Sources like snap shares can contain entries where players played but did not record any meaningful stat, causing that week's record in our main datasets to be absent.
- Player name mismatches can be caused by:
    - Punctuation and suffix differences
    - Renamed players
    - Players not in our alias map
    - PFR/snap imports that do not expose a player id (for example, players with the same name and position)

- Current dropped source-key counts:
```text
snap_counts: 7,810
ff_opp_weekly: 2,544
nextgen_pass_weekly: 327
nextgen_rec_weekly: 998
nextgen_rush_weekly: 403
pfr_pass_weekly: 312
pfr_rush_weekly: 1,151
pfr_rec_weekly: 2,138
pfr_pass_season: 62
pfr_rush_season: 24
pfr_rec_season: 33
```