# Backend

Last verified: 2026-02-22

[![FastAPI](https://img.shields.io/badge/FastAPI-runtime-009688?logo=fastapi&logoColor=white)](api/api.py)
[![SQLite](https://img.shields.io/badge/SQLite-cache-003B57?logo=sqlite&logoColor=white)](database/service/sqlite_service.py)
[![nflreadpy](https://img.shields.io/badge/Data-nflreadpy-1F6FEB)](statistics/statistics.py)

## Table of Contents

1. [Responsibilities](#responsibilities)
2. [Runtime Flow](#runtime-flow)
3. [Module Map](#module-map)
4. [Cache Families](#cache-families)
5. [Run Commands](#run-commands)
6. [Quality Checks](#quality-checks)
7. [Configuration](#configuration)
8. [Detailed Docs](#detailed-docs)

## Responsibilities

- Fetch and process fantasy-relevant NFL data.
- Persist processed caches in SQLite.
- Serve API responses for frontend consumers.

## Runtime Flow

Primary orchestrator: [`app.py`](app.py)

Startup sequence:
1. `App.initialize()` checks for required cache tables.
2. If cache exists: `App.load()` hydrates in-memory data.
3. If cache missing: `App.run()` fetches data, then `App.save()` persists it.

FastAPI lifecycle integration:
- [`api/api.py`](api/api.py) attaches `fantasy_app` to `app.state` during lifespan.
- API startup uses `initialize()` to ensure cache is available.

## Module Map

| Module | Purpose | Entry File |
|---|---|---|
| API | FastAPI app, routers, response models | [`api/api.py`](api/api.py) |
| Statistics | Player/stat cache generation | [`statistics/statistics.py`](statistics/statistics.py) |
| Schedules | Team schedule normalization + BYE insertion | [`schedules/schedules.py`](schedules/schedules.py) |
| Depth charts | ESPN scraper or seasonal nflreadpy depth charts | [`depth_chart/espn.py`](depth_chart/espn.py), [`depth_chart/nrp.py`](depth_chart/nrp.py) |
| Database | SQLite persistence for all cache families | [`database/service/sqlite_service.py`](database/service/sqlite_service.py) |
| Config | Env settings + logging setup | [`config/settings.py`](config/settings.py) |

## Cache Families

Canonical top-level cache names are in [`util/constants.py`](util/constants.py):
- `Statistics`
- `Schedules`
- `ESPNDepthChart`

Statistics cache keys:
- `all_players`
- `by_year`
- `player_weekly_stats`

Persistence service:
- [`database/service/sqlite_service.py`](database/service/sqlite_service.py)

## Run Commands

Install deps:

```bash
uv sync
```

Refresh all data/caches:

```bash
uv run python backend/refresh_data.py
```

Run API:

```bash
uv run python backend/run_api.py
```

Default URL: `http://localhost:8000`

## Quality Checks

Run from repository root:

```bash
uv run ruff check backend
uv run mypy
uv run pytest -q
```

## Configuration

Settings file: [`config/settings.py`](config/settings.py)  
Template: [`../.env.example`](../.env.example)

Variables:
- `API_HOST`
- `API_PORT`
- `CORS_ORIGINS`
- `CORS_ALLOW_CREDENTIALS`
- `DB_PATH`
- `DEPTH_CHART_SOURCE`
- `LOG_LEVEL`
- `LOG_CONSOLE_LEVEL`
- `LOG_DIR`
- `LOG_ROTATION_WHEN`
- `LOG_ROTATION_INTERVAL`
- `LOG_BACKUP_COUNT`
- `TIMING_ENABLED`
- `TIMING_RUN_LOGS_KEEP`

Depth chart source:
- `DEPTH_CHART_SOURCE=espn` uses live ESPN scraping.
- `DEPTH_CHART_SOURCE=nrp` uses seasonal `nflreadpy` depth charts.

Timing logs:
- Standard file logs are separated into subfolders under `LOG_DIR`: `errors/errors.log`, `timing/`.
- With `TIMING_ENABLED=true`, each process run writes to `logs/timing/timing-<timestamp>-pid<pid>.log`.
- `TIMING_RUN_LOGS_KEEP` controls how many of those run files are retained.

## Detailed Docs

- [`api/README.md`](api/README.md)
- [`statistics/README.md`](statistics/README.md)
- [`database/README.md`](database/README.md)
