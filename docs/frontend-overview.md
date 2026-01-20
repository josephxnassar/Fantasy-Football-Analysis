# Frontend Overview

React + Vite single-page app for browsing fantasy football rankings, searching players, and viewing detailed stats.

---

## Table of Contents

- [Stack](#stack)
- [Project Layout](#project-layout)
- [Key Flows](#key-flows)
  - [Rankings](#rankings)
  - [Player Search](#player-search)
  - [Player Details Modal](#player-details-modal)
- [Data Contracts](#data-contracts)
- [Configuration](#configuration)
- [Commands](#commands)
- [Notable Components & Hooks](#notable-components--hooks)
- [Styling](#styling)

---

## Stack
- React 18.2
- Vite 5
- Axios for HTTP
- Vanilla CSS modules per component

---

## Project Layout
```
frontend/
├── src/
│   ├── api.js              # Axios client and endpoints
│   ├── App.jsx             # Root component with tab navigation
│   ├── App.css             # Global layout styles
│   ├── index.css           # Root resets
│   ├── statDefinitions.js  # Stat tooltips, key stat groupings
│   ├── hooks/
│   │   └── usePlayerDetails.js  # Handles fetching and season switching for modal
│   ├── components/
│   │   ├── Rankings.jsx / Rankings.css        # Rankings page
│   │   ├── PlayerSearch.jsx / PlayerSearch.css# Search page
│   │   ├── PlayerDetailsModal.jsx / .css      # Modal with grouped stats
│   │   └── PlayerDetailsModal.css             # Modal styling
│   └── utils/
│       └── helpers.js      # Formatting helpers
├── vite.config.js          # Dev server proxy to backend :8000
├── package.json
└── index.html
```

---

## Key Flows

### Rankings
- Component: `components/Rankings.jsx`
- On mount: `getRankings(format, position)` → `/api/rankings`
- State: `format` (redraft/dynasty), `position` filter, `rankings`, loading/error
- Displays either per-position tables or an overall table
  - Shows `Rating` or `DynastyRating` based on selected format
  - Table simplified to rank, player name, and rating value
- Clicking a player opens details modal with comprehensive percentile breakdown (via `usePlayerDetails`)

### Player Search
- Component: `components/PlayerSearch.jsx`
- Submits `searchPlayers(query)` → `/api/search`
- Displays result cards; clicking a card opens details modal
- Validates min 2 chars; shows error states

### Player Details Modal
- Component: `components/PlayerDetailsModal.jsx`
- Hook: `usePlayerDetails`
  - `getPlayer(name)` for averaged stats + rating
  - `getPlayer(name, season)` for season view; keeps averaged `Rating`
  - Stores `rankingData` passed from Rankings/Search click for percentile display
- **Ratings Section**: Displays dual rating cards with comprehensive percentiles
  - **Redraft Rating Card**: Shows base rating with position and overall percentiles
  - **Dynasty Rating Card**: Shows age-adjusted rating with position and overall percentiles
  - Percentiles formatted as ordinals (e.g., "98th percentile") and capped at 99th
- Grouping: `groupStatsByCategory()` from `statDefinitions.js`
- Key stats highlighted via `isKeyStat`
- Shows available seasons buttons for toggling between career average and individual seasons

---

## Data Contracts
- `getRankings(format, position?)` → `/api/rankings`
  - Returns `{ format, position, model, rankings: { QB: [...], RB: [...], ... } }`
  - Each player entry includes:
    - `name`: Player name
    - `Rating`: Redraft rating
    - `DynastyRating`: Age-adjusted dynasty rating
    - `Age`: Player age
    - `pos_percentile_redraft`: Position percentile (0-100) for redraft
    - `pos_percentile_dynasty`: Position percentile (0-100) for dynasty
    - `overall_percentile_redraft`: Overall percentile (0-100) for redraft
    - `overall_percentile_dynasty`: Overall percentile (0-100) for dynasty
    - All player statistics
- `getPlayer(name, season?)` → `/api/player/{name}`
  - Returns `{ name, position, team, stats, available_seasons }`
  - When season provided, `stats.Rating` stays from averaged call (set in hook)
- `searchPlayers(q, position?)` → `/api/search`
  - Returns `{ query, results: [{ name, position, rating }], count }`

---

## Configuration
- Dev server: `npm run dev` → http://localhost:3000
- API proxy: `vite.config.js` proxies `/api` → `http://localhost:8000`
- Env: `VITE_API_URL` (optional) overrides base URL in `src/api.js`

---

## Commands
- `npm install`          # install deps
- `npm run dev`          # start dev server with proxy
- `npm run build`        # production build
- `npm run preview`      # preview production build

---

## Notable Components & Hooks
- `App.jsx`: two-tab nav (Rankings | Player Search)
- `Rankings.jsx`: format/position filters, overall + per-position views, opens modal
- `PlayerSearch.jsx`: search form, result grid, opens modal
- `PlayerDetailsModal.jsx`: grouped stats, season toggle, rating badge, tooltips
- `usePlayerDetails.js`: manages modal state, fetches averaged + seasonal stats, keeps base rating
- `api.js`: Axios client with `getRankings`, `getPlayer`, `searchPlayers`
- `statDefinitions.js`: tooltip text, key stats per position, category grouping
- `helpers.js`: name extraction, percentile-to-letter grade, ordinal percentile formatting (e.g., "98th percentile" capped at 99th), stat formatting

---

## Styling
- Global layout in `App.css`; resets in `index.css`
- Component-scoped CSS alongside JSX files
- Modal and cards use simple shadows, borders, hover transitions
