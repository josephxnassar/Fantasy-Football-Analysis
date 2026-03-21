# Statistics Layer

Last verified: 03/20/2026

[![nflreadpy](https://img.shields.io/badge/Input-nflreadpy-1F6FEB)](statistics.py)

Generates the statistics cache used by the backend: `all_players`, `seasonal_player_stats`, `weekly_player_stats`, and `meta`.

## Known Issues

- Import sources can contain weeks where players did not record stats or were inactive.
- Player name mismatches can still happen across sources, especially around punctuation, suffixes, renamed players, new players not yet added to the alias map, and PFR/snap imports that do not expose `player_id`.

## Resolved

- Weekly PFR previously had `game_id` merge conflicts when base weekly rows had missing `game_id` values. This was resolved by removing `base_game_id` from weekly PFR joins.
- Seasonal PFR rushing and receiving previously had multi-role position conflicts. This was mostly resolved by removing `base_pos` from those joins.
- Seasonal PFR rushing and receiving previously had `2TM` / `3TM` team conflicts. This is handled by dropping `base_team` when team is not part of the join.
