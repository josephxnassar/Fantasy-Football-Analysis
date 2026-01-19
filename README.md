# NFL Fantasy Football Analysis Tool

Full-stack analysis tool for collecting, processing, and analyzing NFL player depth charts and statistics. Features both a Python backend API (FastAPI) and a React frontend for interactive player rankings with detailed stats.

## ⚙️ Prerequisites

**Required Software:**
- **Python 3.8+** - Backend API and data processing
- **Node.js 16+** - Frontend development and build tooling
  - Download from [nodejs.org](https://nodejs.org/)
  - npm comes bundled with Node.js

**Why Virtual Environment?**

This project uses a Python virtual environment (venv) because `nfl_data_py` requires specific versions of pandas (1.5.3) and numpy (1.23.5). Using venv keeps these dependencies isolated from your system Python, preventing version conflicts with other projects.

---

## 📂 Modules

### 1. [`Statistics`](./backend/statistics/statistics.py)
Processes NFL seasonal data by organizing into position and running ridge regression for rating calculations.

### 2. [`Schedules`](./backend/schedules/schedules.py)
Processes NFL schedule data by inserting bye weeks where games are missing from the schedule.

### 3. [`ESPNDepthChart`](./backend/depth_chart/espn.py)
Scrapes player depth chart information directly from ESPN's website for current depth positioning.

---

## ▶️ Running the Program

### Quick Start (Recommended)

**⚠️ Prerequisites:** Ensure you have **Node.js 16+** and **Python 3.8+** installed before proceeding.

Run both backend and frontend servers with one command:

**Windows (PowerShell):**

First, navigate to the project root directory:

```powershell
.\dev-startup.ps1
```

This will open two terminal windows:
- **Backend API**: `http://localhost:8000` (FastAPI with hot-reload)
- **Frontend**: `http://localhost:3000` (React + Vite dev server)

**To stop:** Press `Ctrl+C` in each terminal.

---

### Manual Setup (If needed)

#### 1. � Create Virtual Environment (Recommended)

Create and activate a Python virtual environment to isolate project dependencies:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when activated. To deactivate later, simply run:
```bash
deactivate
```

#### 2. 📦 Install Backend Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

Required Python packages:
- `pandas`
- `scikit-learn`
- `beautifulsoup4`
- `requests`
- `nfl_data_py`
- `fastapi`
- `uvicorn`
- `pydantic`

**Note:** Always activate your virtual environment before installing dependencies or running the backend.

#### 3. 🎨 Install Frontend Dependencies

**⚠️ REQUIRED:** You must have **Node.js 16+** installed to run the frontend.
- Download from [nodejs.org](https://nodejs.org/) if not already installed
- npm is included automatically with Node.js
- Verify installation: `node --version` and `npm --version`

```bash
cd frontend
npm install
```

This will install React 18.2, Vite, Axios, and all other frontend dependencies.

#### 4. 🚀 Start Backend API

Ensure your virtual environment is activated, then:

```bash
python run_api.py
```

Backend will run on `http://localhost:8000` with auto-reload enabled.

#### 5. 🎨 Start Frontend Dev Server

In a new terminal, from the project root:

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`.

---

## 📁 Project Structure

```
backend/              # Backend Python code (FastAPI)
├── api.py           # FastAPI app with all endpoints
├── app.py           # Core App class
├── models.py        # Pydantic response schemas
├── depth_chart/     # Player depth chart sources
│   └── espn.py     # ESPN depth chart scraper
├── statistics/      # Player rating calculations
│   └── ratings/
├── schedules/       # NFL schedule data processing
├── database/        # SQLite cache layer
│   ├── DAO/
│   └── service/
├── util/            # Constants and helpers
└── base_source.py   # Base class for data sources

frontend/            # React + Vite frontend
├── src/
│   ├── api.js       # Axios HTTP client
│   ├── App.jsx      # Main component
│   ├── App.css      # Global styles
│   └── components/  # Page components
│       ├── Rankings.jsx
│       ├── Rankings.css
│       ├── PlayerSearch.jsx
│       └── PlayerSearch.css
├── vite.config.js   # Vite config with API proxy
└── package.json

config/              # Logging configuration
tests/               # Python unit tests
dev-startup.ps1      # One-command startup script
run_api.py           # FastAPI server entry point
requirements.txt     # Python dependencies
```

---

## 💻 Backend API

### Endpoints

Base URL: `http://localhost:8000`

- `GET /api/rankings` - Get player rankings with filters (format, position)
- `GET /api/player/{player_name}` - Get detailed player stats and position/team info
- `GET /api/search?q=query` - Search players by name

All endpoints support CORS for frontend integration.

---

## 🎨 React Frontend

### Features

- **Rankings**: View player rankings with customizable filters (format, position)
- **Player Details**: Click any player name to see detailed stats and team information
- **Player Search**: Search and view player statistics by position

### Tech Stack

- **React 18.2** - UI framework
- **Vite 5.0** - Build tool with dev server
- **Axios** - HTTP client for API calls
- **CSS Grid/Flexbox** - Responsive layouts

### Environment Variables

The frontend uses Vite's environment system (`VITE_` prefix):
- `VITE_API_URL` - Backend API base URL (default: `http://localhost:8000`)

Configured in `frontend/vite.config.js` with API proxy for development.

---

## 📚 Documentation

Complete documentation in the `docs/` folder:

- [`README.md`](./docs/README.md) - Backend architecture and data flow overview
- [`frontend-overview.md`](./docs/frontend-overview.md) - React frontend structure, flows, and contracts
- [`backend-api.md`](./docs/backend-api.md) - REST API endpoint reference
- [`backend-statistics.md`](./docs/backend-statistics.md) - Statistics processor and rating algorithms
- [`backend-schedules.md`](./docs/backend-schedules.md) - Schedule data processing and bye weeks
- [`backend-depth-charts.md`](./docs/backend-depth-charts.md) - ESPN depth chart scraping
- [`backend-import-seasonal-data.md`](./docs/backend-import-seasonal-data.md) - Data column definitions and mappings

---

## 👨‍💻 Author

Created by Joseph Nassar, 2025
