# Database Layer

Last verified: 2026-02-22

[![SQLite](https://img.shields.io/badge/SQLite-persistence-003B57?logo=sqlite&logoColor=white)](service/sqlite_service.py)

SQLite cache persistence for `Statistics`, `Schedules`, and `ESPNDepthChart`.

## Table of Contents

1. [Components](#components)
2. [Storage Rules](#storage-rules)
3. [Load Rules](#load-rules)
4. [Cache Presence Gate](#cache-presence-gate)
5. [Database Path](#database-path)
6. [Practical Commands](#practical-commands)

## Components

| Layer | File | Responsibility |
|---|---|---|
| DAO | [`DAO/sqlite_dao.py`](DAO/sqlite_dao.py) | Raw table operations |
| Service | [`service/sqlite_service.py`](service/sqlite_service.py) | Cache-family-specific save/load orchestration |

## Storage Rules

`SQLService.save_to_db(cache, cls_name)` branches by cache family:

| Cache Family | Stored Shape |
|---|---|
| `Statistics` | `all_players`, per-season/per-position tables, weekly stats |
| `Schedules` | One table per `season + team` |
| `ESPNDepthChart` | One table per team |

Statistics weekly rows are flattened with an internal key column (`__player_key`) so cache grouping is stable on reload.

## Load Rules

`SQLService.load_from_db(keys, cls_name)` reconstructs runtime cache structures expected by API routes:

- Statistics:
  - `all_players`
  - `by_year`
  - `player_weekly_stats`
- Schedules:
  - `{season: {team: DataFrame}}`
- Depth charts:
  - `{team: DataFrame}`

## Cache Presence Gate

`SQLService.has_cached_data()` returns true only if:
- `Statistics_all_players` exists
- at least one `Schedules_*` table exists
- at least one `ESPNDepthChart_*` table exists

If false, required cache families are missing and startup should trigger a cache rebuild via `App.initialize()`.

## Database Path

Configured by `DB_PATH` in settings (`backend/config/settings.py`).

Default:
- `backend/database/data/nfl_cache.db`

## Practical Commands

Rebuild and persist:

```bash
uv run python backend/refresh_data.py
```

Run API (loads cache if present, otherwise rebuilds cache):

```bash
uv run python backend/run_api.py
```
