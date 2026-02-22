# API Layer

Last verified: 2026-02-22

[![FastAPI](https://img.shields.io/badge/FastAPI-routes-009688?logo=fastapi&logoColor=white)](api.py)
[![Pydantic](https://img.shields.io/badge/Pydantic-models-E92063)](models.py)

FastAPI routers that expose cache-backed fantasy data from `App.caches`.

## Table of Contents

1. [Source Map](#source-map)
2. [Startup Contract](#startup-contract)
3. [Endpoint Index](#endpoint-index)
4. [Error Mapping](#error-mapping)
5. [Response Models](#response-models)

## Source Map

| Area | File |
|---|---|
| App + lifespan + middleware | [`api.py`](api.py) |
| Response schemas | [`models.py`](models.py) |
| Statistics routes | [`routes/statistics_routes.py`](routes/statistics_routes.py) |
| Schedule routes | [`routes/schedule_routes.py`](routes/schedule_routes.py) |
| Depth chart routes | [`routes/depth_chart_routes.py`](routes/depth_chart_routes.py) |
| Team metadata routes | [`routes/teams_routes.py`](routes/teams_routes.py) |
| Route helper utils | [`util/`](util) |

## Startup Contract

During lifespan in [`api.py`](api.py):
1. Build `App()`
2. Call `initialize()`
3. Attach to `request.app.state.fantasy_app`

Behavior:
- Existing DB cache -> load into memory
- Missing DB cache -> fetch fresh source data, persist cache, and load into memory

Routes rely on these caches and surface `503` when required caches are unavailable.

Statistics route behavior:
- `/api/player/{player_name}` matches the provided player name directly against stats cache player names.
- JSON-safe numeric cleanup is handled in the statistics pipeline output (not in API route code).

## Endpoint Index

Local base URL: `http://localhost:8000`

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | API status |
| `GET` | `/api/player/{player_name}` | Player profile + stats + weekly data |
| `GET` | `/api/search` | Name search (optional position filter) |
| `GET` | `/api/chart-data` | Chart payload by position/season |
| `GET` | `/api/teams/divisions` | Division + team-name metadata |
| `GET` | `/api/schedules/{team}` | Team schedule by season |
| `GET` | `/api/depth-charts/{team}` | Team depth chart |

Interactive docs (FastAPI defaults):
- `/docs`
- `/redoc`

## Error Mapping

Custom exception handlers in [`api.py`](api.py):

| Exception | HTTP |
|---|---|
| `CacheNotLoadedError` | `503` |
| `PlayerNotFoundError` | `404` |
| `FantasyFootballError` | `500` |

Validation and input errors are raised as `HTTPException` (`400`/`404`).

## Response Models

Canonical model definitions and examples:
- [`models.py`](models.py)
