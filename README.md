# Fantasy Football Analysis

Last verified: 2026-02-22

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](backend/api/api.py)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](frontend/package.json)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](frontend/vite.config.js)
[![SQLite](https://img.shields.io/badge/SQLite-Cache-003B57?logo=sqlite&logoColor=white)](backend/database/service/sqlite_service.py)

Full-stack NFL fantasy analysis app with a FastAPI backend and React frontend for:
- Player profile + weekly stat breakdowns
- Advanced stat exploration (EPA, air-yards share, WOPR, etc.)
- Team schedules and depth charts
- Chart-ready seasonal stat exploration
- Stats-layer player-name alias resolution (for suffix variants like `III`, `Jr`, etc.)

## Table of Contents

1. [Architecture At A Glance](#architecture-at-a-glance)
2. [Quick Start](#quick-start)
3. [Core Commands](#core-commands)
4. [Quality Checks](#quality-checks)
5. [Configuration](#configuration)
6. [CI (GitHub Actions)](#ci-github-actions)
7. [Commit Template](#commit-template)
8. [Documentation Map](#documentation-map)
9. [Repository Layout](#repository-layout)

## Architecture At A Glance

```text
nflreadpy + ESPN
      |
      v
backend data modules
(statistics, schedules, depth chart)
      |
      v
SQLite cache (DB_PATH)
      |
      v
FastAPI (/api/*)
      |
      v
React + Vite UI
```

Key backend entrypoints:
- App orchestration: [`backend/app.py`](backend/app.py)
- API server start: [`backend/run_api.py`](backend/run_api.py)
- Data refresh: [`backend/refresh_data.py`](backend/refresh_data.py)

## Quick Start

Prerequisites:
- `uv`
- Node.js + npm

Windows one-command startup:

```powershell
.\dev-startup.ps1
```

Manual startup:

```bash
uv sync
cd frontend
npm install
cd ..
uv run python backend/run_api.py
```

Then in a second terminal:

```bash
cd frontend
npm run dev
```

Default local URLs:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Core Commands

Install backend dependencies:

```bash
uv sync
```

Refresh all caches from source data:

```bash
uv run python backend/refresh_data.py
```

Run backend:

```bash
uv run python backend/run_api.py
```

Run frontend:

```bash
cd frontend
npm run dev
```

## Quality Checks

Static analysis configuration files:
- Python (`ruff`, `mypy`): [`pyproject.toml`](pyproject.toml)
- Frontend (`eslint`): [`frontend/eslint.config.js`](frontend/eslint.config.js)

Backend quality checks:

```bash
uv run ruff check backend
uv run mypy
uv run pytest -q
```

Frontend quality checks:

```bash
cd frontend
npm run lint
npm run test:run
npm run build
```

## Configuration

Environment template: [`.env.example`](.env.example)

Backend variables (loaded by [`backend/config/settings.py`](backend/config/settings.py)):

| Variable | Default | Purpose |
|---|---|---|
| `API_HOST` | `0.0.0.0` | API bind host |
| `API_PORT` | `8000` | API bind port |
| `CORS_ORIGINS` | `*` | Allowed origins |
| `CORS_ALLOW_CREDENTIALS` | `false` | Enable credentialed CORS only when origins are explicit |
| `DB_PATH` | `backend/database/data/nfl_cache.db` | SQLite location |
| `LOG_LEVEL` | `DEBUG` | Root logging level |

Frontend variable:
- `VITE_API_URL` (default: `http://localhost:8000/api`)

## CI (GitHub Actions)

Workflow file: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

Triggers:
- Push to `main` or `dev`
- Pull request into `main` or `dev`
- Manual run (`workflow_dispatch`)

Checks:
- Backend lint/type/tests on Python `3.10` and `3.11`:
  - `uv run ruff check backend`
  - `uv run mypy`
  - `uv run pytest -q`
- Frontend lint/tests/build:
  - `npm run lint`
  - `npm run test:run`
  - `npm run build`

## Commit Template

Template file: [`.gitmessage.txt`](.gitmessage.txt)

Enable locally:

```bash
git config commit.template .gitmessage.txt
```

Optional (all repos on your machine):

```bash
git config --global commit.template "C:/path/to/.gitmessage.txt"
```

## Documentation Map

| Area | README |
|---|---|
| Backend overview | [`backend/README.md`](backend/README.md) |
| API routes/models/errors | [`backend/api/README.md`](backend/api/README.md) |
| Statistics pipeline | [`backend/statistics/README.md`](backend/statistics/README.md) |
| SQLite cache layer | [`backend/database/README.md`](backend/database/README.md) |
| Frontend architecture | [`frontend/README.md`](frontend/README.md) |

## Repository Layout

```text
backend/
  api/            FastAPI app, routes, models, API helpers
  statistics/     nflreadpy ingestion + stat cache generation
  schedules/      schedule normalization + bye-week filling
  depth_chart/    ESPN depth chart scraper
  database/       SQLite DAO/service cache persistence
  config/         env loading and logging config
frontend/
  src/            React components, hooks, utils
  public/         static assets
dev-startup.ps1   Windows bootstrap/start script
pyproject.toml    Python deps/project metadata
frontend/package.json  frontend deps/scripts
```
