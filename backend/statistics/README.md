# Statistics Layer

Last verified: 03/20/2026

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates the statistics cache used by the backend: `all_players`, `seasonal_player_stats`, `weekly_player_stats`, and `meta`.

## Known Issues

- Import sources can contain weeks where players did not record stats or were inactive.
- Player name mismatches can still happen across sources, especially around punctuation, suffixes, renamed players, new players not yet added to the alias map, and PFR/snap imports that do not expose `player_id`.