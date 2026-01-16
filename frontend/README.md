# Fantasy Football Analysis Frontend

React + Vite frontend for the Fantasy Football Analysis tool.

## Setup

```bash
npm install
npm run dev
```

The frontend will run on `http://localhost:3000` and proxy API requests to `http://localhost:8000`.

## Configuration

**Important:** This project uses **Vite**, not Create React App. Environment variables must use the `VITE_` prefix.

Environment variables are defined in `vite.config.js`:
- `VITE_API_URL` - Backend API base URL (default: `http://localhost:8000`)

## Features

- **Rankings** - Player rankings with format/position/model filtering
- **Player Search** - Search players and view detailed stats
- **Streaming Recommendations** - Weekly suggestions by position
- **Defense Matchups** - Tier-based opponent analysis

## Development

Key files:
- `src/api.js` - Axios client for backend API calls
- `src/App.jsx` - Main component with tab navigation
- `src/components/` - Individual page components
- `vite.config.js` - Vite configuration with API proxy

## Build for Production

```bash
npm run build
npm run preview
```
