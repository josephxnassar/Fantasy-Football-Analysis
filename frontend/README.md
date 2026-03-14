# Frontend

Last verified: 2026-03-13

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](package.json)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)](vite.config.js)
[![Axios](https://img.shields.io/badge/Axios-HTTP-5A29E4)](src/api.js)
[![Recharts](https://img.shields.io/badge/Recharts-Charts-22C55E)](src/components/charts/Charts.jsx)

React + Vite client for browsing player statistics, schedules, depth charts, charts, and player details from the backend API.

## Table of Contents

1. [Run Locally](#run-locally)
2. [Quality Checks](#quality-checks)
3. [Environment And Proxy](#environment-and-proxy)
4. [UI Navigation Model](#ui-navigation-model)
5. [Key Source Paths](#key-source-paths)
6. [Build](#build)

## Run Locally

```bash
npm install
npm run dev
```

Default URL: `http://localhost:3000`

## Quality Checks

```bash
npm run lint
npm run test:run
npm audit
npm run build
```

Test setup and layout:
- Shared Vitest setup lives in [`tests/setup.js`](tests/setup.js).
- Tests are grouped into [`tests/components/`](tests/components), [`tests/hooks/`](tests/hooks), and [`tests/utils/`](tests/utils).
- [`tests/deferred.js`](tests/deferred.js) is the only shared async helper.
- If `npm run test:run` fails before executing tests, align the `vite` and `vitest` versions in [`package.json`](package.json).

## Environment And Proxy

- API base override: `VITE_API_URL` (default `http://localhost:8000/api`)
- Dev proxy config: [`vite.config.js`](vite.config.js)
  - `/api` -> `http://localhost:8000`

## UI Navigation Model

The app opens on a **Landing Page** ([`src/components/landing/LandingPage.jsx`](src/components/landing/LandingPage.jsx)) with quick search, feature cards, at-a-glance stats, and data source attribution. A Home button in the header returns to the landing page.

[`src/App.jsx`](src/App.jsx) owns a single shared player-details modal that is reused by landing-page search, statistics search, and charts. The modal flow lives in [`src/components/player-details/`](src/components/player-details), and the modal's team depth chart loads on demand only when the **Depth Chart** tab is opened.
The modal stat grouping suppresses `pfr_pass_on_tgt_pct` when the value is `0` to avoid showing placeholder values for seasons where that metric is missing in source data.

Top-level tabs in [`src/App.jsx`](src/App.jsx):
- `Statistics`
- `Schedules`
- `Depth Charts`

Statistics sub-tabs in [`src/components/statistics/Statistics.jsx`](src/components/statistics/Statistics.jsx):
- Charts
- Rankings (category + stat weighted scoring)
- Player Comparison (up to 3 player-season columns with production-profile stat rows)
- Player Search

Charts tab views in [`src/components/charts/Charts.jsx`](src/components/charts/Charts.jsx):
- Leaderboard (horizontal bar)
- Average vs Upside scatter
- Season Trends line (single selected player)

Charts and Rankings remember key control selections for the current browser session (for example, chart view, position/top-N, selected stat, trend player, and ranking weights) via `sessionStorage`. Individual chart views are loaded on demand from the charts feature folder rather than bundled into one large feature entry chunk.

Schedules and Depth Charts share the same team navigation pattern via [`src/components/team-browser/TeamBrowser.jsx`](src/components/team-browser/TeamBrowser.jsx):
- Division Browser
- Team Search

## Key Source Paths

| Area | File/Folder |
|---|---|
| API wrapper | [`src/api.js`](src/api.js) |
| App shell | [`src/App.jsx`](src/App.jsx), [`src/components/app/`](src/components/app) |
| Shared hooks | [`src/hooks/`](src/hooks) |
| Feature components | [`src/components/`](src/components) |
| Charts feature | [`src/components/charts/`](src/components/charts) |
| Statistics feature | [`src/components/statistics/`](src/components/statistics) |
| Rankings feature | [`src/components/rankings/`](src/components/rankings) |
| Comparison feature | [`src/components/comparison/`](src/components/comparison) |
| Team browser feature | [`src/components/team-browser/`](src/components/team-browser) |
| Player search feature | [`src/components/player-search/`](src/components/player-search) |
| Reusable components | [`src/components/common/`](src/components/common) |
| Landing page sub-components | [`src/components/landing/`](src/components/landing) |
| Shared player modal flow | [`src/App.jsx`](src/App.jsx), [`src/components/player-details/usePlayerDetails.js`](src/components/player-details/usePlayerDetails.js), [`src/components/player-details/PlayerDetailsModal.jsx`](src/components/player-details/PlayerDetailsModal.jsx) |
| Player modal sub-components | [`src/components/player-details/`](src/components/player-details) |
| Shared app copy | [`src/appContent.js`](src/appContent.js) |
| Utilities | [`src/utils/`](src/utils) |
| Stat utilities | [`src/utils/statDefinitions.js`](src/utils/statDefinitions.js), [`src/utils/statMeta.js`](src/utils/statMeta.js), [`src/utils/statGrouping.js`](src/utils/statGrouping.js), [`src/utils/statColorHelpers.js`](src/utils/statColorHelpers.js) |
| Feature config | [`src/components/statistics/statisticsOptions.js`](src/components/statistics/statisticsOptions.js), [`src/components/rankings/rankingGroups.js`](src/components/rankings/rankingGroups.js) |
| Tests | [`tests/`](tests), [`tests/setup.js`](tests/setup.js) |
| Global styles/tokens | [`src/index.css`](src/index.css) |

## Build

```bash
npm run build
npm run preview
```
