# Backend Documentation

Complete documentation for the Fantasy Football Analysis backend system.

---

## Overview

The backend is a Python-based system that collects, processes, and serves NFL player data through a REST API. It consists of three main data collection modules and a FastAPI server.

### Architecture Diagram:

```
Data Sources (NFL API, ESPN)
         ↓
┌─────────────────────────────────────┐
│  Data Collection Modules            │
├─────────────────────────────────────┤
│  • Statistics (ratings via ML)       │
│  • Schedules (bye week handling)     │
│  • ESPNDepthChart (web scraping)     │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  SQLite Cache Database              │
│  (nfl_cache.db)                     │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  FastAPI Server (api.py)            │
│  Port: 8000                         │
└─────────────────────────────────────┘
         ↓
   React Frontend (port 3000)
```

---

## Documentation Files

### 1. [statistics.md](./statistics.md)
**Purpose**: Player ratings and seasonal statistics processing

**Key Components**:
- Ridge Regression model for generating player ratings
- Career-averaged statistics
- Individual season statistics
- Player age tracking for dynasty format
- Active player filtering

**Main Class**: `Statistics`

**Entry Point**: `backend/statistics/statistics.py`

---

### 2. [schedules.md](./schedules.md)
**Purpose**: NFL schedule data collection and organization

**Key Components**:
- Regular season schedule fetching
- Team-specific schedule organization
- Bye week insertion
- Team name standardization

**Main Class**: `Schedules`

**Entry Point**: `backend/schedules/schedules.py`

---

### 3. [espn.md](./espn.md)
**Purpose**: Real-time team depth chart scraping

**Key Components**:
- ESPN website scraping
- Player depth positioning
- Offensive position extraction
- Status indicator removal

**Main Class**: `ESPNDepthChart`

**Entry Point**: `backend/depth_chart/espn.py`

---

### 4. [api.md](./api.md)
**Purpose**: REST API endpoint documentation

**Key Endpoints**:
- `GET /api/rankings` - Player rankings with filters
- `GET /api/player/{name}` - Detailed player stats
- `GET /api/search` - Player search

**Server**: FastAPI on port 8000

**Entry Point**: `backend/api.py`

---

### 5. [import_seasonal_data.md](./import_seasonal_data.md)
**Purpose**: Reference documentation for `nfl_data_py` data columns

**Includes**:
- Market share metrics definitions
- Advanced efficiency metrics
- Column name mappings

---

## Data Flow

### 1. Data Collection (`refresh_data.py`)
```
App.run()
  ├── ESPNDepthChart().run()    → Fetches current depth charts
  ├── Schedules().run()          → Loads schedule data
  └── Statistics().run()         → Processes stats & generates ratings
         ↓
      All data → Cache objects
```

### 2. Data Persistence
```
App.save()
  ├── SQLService.save_to_db()
  └── Saves each module's cache → SQLite database
```

### 3. API Server (`run_api.py`)
```
FastAPI startup
  ├── App.load() → Loads cached data from database
  └── Serves REST endpoints
```

### 4. Frontend Integration
```
React app calls API endpoints
  ├── Fetches rankings
  ├── Retrieves player details
  └── Searches for players
```

---

## Key Design Patterns

### BaseSource Pattern
All data collection modules inherit from `BaseSource`:
- Standardized cache management
- Abstract `_load()` and `run()` methods
- Consistent error handling

### Dynasty vs Redraft
- **Redraft**: Uses raw player ratings
- **Dynasty**: Applies age-based multipliers using `dynasty_ratings.py`
  - Young RBs get boost (before peak age 24)
  - Veterans past prime get steep decline
  - Position-specific age curves

### Cache Structure
Multi-level caching approach:
```
Statistics Cache:
{
  'averaged': {pos → DataFrame},    # Career stats with ratings
  'by_year': {season → {pos → DataFrame}},  # Individual season stats
  'available_seasons': [list],
  'eligible_players': {set},
  'player_ages': {dict}
}

Schedules Cache:
{team → DataFrame, ...}

ESPNDepthChart Cache:
{team → DataFrame, ...}
```

---

## Configuration

### Environment
- **Python**: 3.8+
- **Port**: 8000 (API), 3000 (Frontend)
- **Database**: SQLite (`nfl_cache.db`)

### Dependencies
Core packages:
- `pandas` - Data manipulation
- `scikit-learn` - Ridge Regression
- `nfl_data_py` - NFL data API
- `fastapi`, `uvicorn` - Web server
- `beautifulsoup4`, `requests` - Web scraping

### Season Configuration
- `STATISTICS_SEASONS`: Historical data years (2016-2024)
- `CURRENT_SEASON`: 2025 (for depth charts & schedules)
- Configurable in `backend/util/constants.py`

---

## Error Handling

### Logging
- **Console**: INFO and above
- **File**: `errors.log` (errors only)
- Configured in `config/logging_config.py`

### Module-Level Error Recovery
- Each module logs errors per item without stopping
- `Statistics`: Logs player processing errors, continues with others
- `Schedules`: Logs team errors, continues with others
- `ESPNDepthChart`: Logs team scraping errors, continues with others

### API Error Responses
- 400: Bad request (validation errors)
- 404: Not found (player not in cache)
- 503: Service unavailable (data not loaded)
- 500: Server error

---

## Performance Considerations

### Caching
- All data cached in SQLite on first run
- Subsequent API calls use cached data (instant response)
- Cache expires when app restarts (requires `refresh_data.py`)

### Rating Computation
- Ridge Regression fitted once per position
- Scaled features using StandardScaler
- Ratings cached, not recomputed per request

### Web Scraping
- ESPN scraping only on data refresh, not on each API call
- Concurrent requests may timeout (consider rate limiting for production)

---

## Deployment Considerations

### Production Checklist
- [ ] Restrict CORS `allow_origins` to frontend domain
- [ ] Implement rate limiting on API endpoints
- [ ] Add authentication/authorization if needed
- [ ] Move database path to environment variable
- [ ] Add database backup strategy
- [ ] Monitor ESPN scraping (may require User-Agent rotation)
- [ ] Set up periodic cache refresh (cron job)

### Scaling Options
- Load database from file or cloud storage
- API gateway with caching layer
- Separate worker processes for data refresh
- Message queue for data collection jobs

---

## Troubleshooting

### "Statistics data not loaded"
- Run `python refresh_data.py` first
- Check if `nfl_cache.db` exists
- Verify internet connection

### No players returned in rankings
- Check `eligible_players` filtering (active vs retired)
- Verify season configuration in constants
- Ensure statistics data was cached

### ESPN depth chart errors
- ESPN HTML structure may have changed
- Update `_parse_soup()` method if scraping fails
- Check User-Agent header if requests are blocked

### Missing player in search
- Player may not be active in latest season
- Check spelling and capitalization
- Verify player played in data seasons (2016-2024)

---

## Quick References

### Column Naming
Internal → Display (examples):
- `passing_yards` → `Pass Yds`
- `receiving_tds` → `Rec TD`
- `fantasy_points_ppr` → `PPR Pts`

See full mapping in `backend/util/constants.py` (`COLUMN_NAME_MAP`)

### Positions
- QB: Quarterback
- RB: Running Back
- WR: Wide Receiver
- TE: Tight End

### Valid Formats
- `redraft`: Current season focused
- `dynasty`: Career longevity focused

---

## Related Files

- `backend/app.py` - Main orchestration class
- `backend/api.py` - FastAPI application
- `backend/models.py` - Pydantic request/response schemas
- `backend/database/` - SQLite cache layer
- `backend/util/` - Constants, helpers, dynasty ratings
- `refresh_data.py` - Data collection entry point
- `run_api.py` - API server entry point
