# AI Agent Instructions for Fantasy Football Analysis

## Project Overview
Full-stack NFL player analysis tool combining Python backend (FastAPI) for data processing and React/Vite frontend for interactive rankings. Three core modules ingest ESPN depth charts, seasonal stats, and schedule data; ratings calculated via ridge regression and served through REST API.

## Architecture & Data Flow

### Backend Pipeline
1. **Data Ingestion** (`backend/app.py`): `App` orchestrates three sources:
   - `ESPNDepthChart` - Web scrapes depth positioning from ESPN team pages
   - `Schedules` - Fetches and normalizes NFL schedule data, inserting bye weeks
   - `Statistics` - Pulls historical stats from `nfl_data_py`, groups by position/season

2. **Processing**:
   - All modules inherit from `BaseSource` (contract: `run()`, `get_cache()`, `get_keys()`)
   - Data cached in-memory as position-keyed DataFrames (e.g., `cache['WR']`)
   - `Statistics` applies `RidgeRegression` ratings to normalized stat columns via `backend/statistics/ratings/regression.py`

3. **Persistence**: `SQLiteCacheManager` (DAO pattern) serializes cache to `nfl_cache.db` per source name

### API Layer (`backend/api.py`)
- FastAPI app loads cache on startup, endpoints query by position/format
- Redraft prioritizes current season; dynasty weights historical
- Integer stats formatted without decimals (see `INTEGER_STATS` set)
- CORS enabled for frontend; Pydantic models enforce response shape

### Frontend Architecture
- React with Vite: `Rankings` component fetches `/api/rankings`, `PlayerSearch` queries `/api/search`
- `api.js` centralizes axios calls with `VITE_API_URL` env override
- Components in `src/components/`, hooks in `src/hooks/`, utilities in `src/utils/`

## Key Patterns & Conventions

**Data Keys**: All DataFrame indices and cache keys use standard NFL codes: positions `['QB', 'RB', 'WR', 'TE']`, teams from `constants.TEAMS` (32 codes like 'KC', 'GB')

**Column Naming**: Statistics module maps nfl_data_py's snake_case columns to display names via `COLUMN_NAME_MAP`. Always use mapped names in API responses; raw names only in internal processing.

**Environment Setup**: Virtual environment **required**—`nfl_data_py` pins pandas 1.5.3, numpy 1.23.5. Activate via `.\venv\Scripts\Activate.ps1` (Windows).

**One-Command Startup**: Run `.\dev-startup.ps1` to launch backend (FastAPI, hot-reload, port 8000) and frontend (Vite, port 3000) in separate terminals simultaneously.

## Critical Developer Workflows

1. **Add Statistics Column**: Map name in `COLUMN_NAME_MAP`, add to `INTEGER_STATS` if whole number, add display in Rankings component
2. **Extend Depth Chart Scraping**: Modify ESPN parsing logic in `_parse_soup()` or URL pattern in `_get_soup()`
3. **Change Regression Model**: Replace ridge logic in `backend/statistics/ratings/regression.py`, update API format selector
4. **Add API Endpoint**: Create Pydantic model in `backend/models.py`, implement handler in `backend/api.py`, ensure CORS allows frontend

## Testing & Debugging
- Unit tests in `tests/` (ESPN, schedules, statistics modules)
- Run: `pytest` (requires `pytest`, `pytest-mock` from requirements.txt)
- Enable logging via `config/logging_config.py`; debug print statements in data processing modules

## External Dependencies & Integration Points
- `nfl_data_py`: Season data source (2016–2024 supported in `STATISTICS_SEASONS`)
- ESPN website: Scrape-dependent depth charts (headers required to bypass blocking)
- SQLite: Local cache DB (no schema migration tools—manual if structure changes)
- Axios: Frontend HTTP client; configure API base URL via VITE_API_URL

## Common Pitfalls
- **Cache Invalidation**: After modifying data sources, delete `nfl_cache.db` to force reload
- **Column Mismatches**: If stats column missing from display, check both `COLUMN_NAME_MAP` and API response handling
- **CORS Issues**: Ensure API CORS allows frontend origin (currently open but restrict in production)
- **Virtual Environment**: Forgetting to activate `.venv` causes dependency import errors
