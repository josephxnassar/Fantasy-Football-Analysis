# Statistics Layer

Last verified: 03/20/2026

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates the statistics cache used by the backend: `all_players`, `seasonal_player_stats`, `weekly_player_stats`, and `meta`.

## Known Issues

### Merge Conflicts

- Weeks in which players are inactive do not create a record.
- Sources like snap shares can contain entries where players played but did not record any meaningful stat, causing that week's record in our main datasets to be absent.
- Player name mismatches can be caused by:
    - Punctuation and suffix differences
    - Renamed players
    - Players not in our alias map
    - PFR/snap imports that do not expose a player id (for example, players with the same name and position)