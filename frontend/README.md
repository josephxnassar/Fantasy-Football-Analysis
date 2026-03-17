# Frontend

Last verified: 2026-03-17

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](package.json)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)](vite.config.js)
[![Axios](https://img.shields.io/badge/Axios-HTTP-5A29E4)](src/api/index.js)
[![Recharts](https://img.shields.io/badge/Recharts-Charts-22C55E)](src/features/statistics/charts/Charts.jsx)

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
npm run format:check
npm run test:run
npm audit
npm run build
```

Apply formatting locally with `npm run format`.

Test setup and layout:

- Shared Vitest setup lives in [`tests/support/setup.js`](tests/support/setup.js).
- Tests mirror the source layout through [`tests/app/`](tests/app), [`tests/features/`](tests/features), and [`tests/shared/`](tests/shared).
- [`tests/support/deferred.js`](tests/support/deferred.js) is the shared async helper.
- If `npm run test:run` fails before executing tests, align the `vite` and `vitest` versions in [`package.json`](package.json).

CSS ownership:

- Keep CSS close to the component or feature that owns it.
- Use small package-level shared styles only when they represent one clearly owned visual language, not a general dumping ground.
- [`src/app/App.css`](src/app/App.css) owns app-level layout and tab navigation.
- [`src/app/shell/Shell.css`](src/app/shell/Shell.css) owns shell-only chrome, previews, and tab error styling.
- [`src/app/brand/brand.css`](src/app/brand/brand.css) owns the shared header/home hero visual language.
- Feature-local visuals stay in the feature folder, for example [`src/features/home/HeroSection.css`](src/features/home/HeroSection.css).

## Environment And Proxy

- API base override: `VITE_API_URL` (default `http://localhost:8000/api`)
- Dev proxy config: [`vite.config.js`](vite.config.js)
  - `/api` -> `http://localhost:8000`

## UI Navigation Model

The app opens on a **Home Page** ([`src/features/home/HomePage.jsx`](src/features/home/HomePage.jsx)) with quick search, feature cards, at-a-glance stats, and data source attribution. A Home button in the header returns to the home page.

[`src/app/App.jsx`](src/app/App.jsx) owns a single shared player-details modal that is reused by home-page search, statistics search, and charts. The modal flow lives in [`src/features/statistics/player-details/`](src/features/statistics/player-details), and the modal's team depth chart loads on demand only when the **Depth Chart** tab is opened.
The modal stat grouping suppresses `pfr_pass_on_tgt_pct` when the value is `0` to avoid showing placeholder values for seasons where that metric is missing in source data.

Top-level tabs in [`src/app/App.jsx`](src/app/App.jsx):

- `Statistics`
- `Schedules`
- `Depth Charts`

Statistics sub-tabs in [`src/features/statistics/Statistics.jsx`](src/features/statistics/Statistics.jsx):

- Charts
- Rankings (category + stat weighted scoring)
- Player Comparison (up to 3 player-season columns with production-profile stat rows)
- Player Search

Charts tab views in [`src/features/statistics/charts/Charts.jsx`](src/features/statistics/charts/Charts.jsx):

- Leaderboard (horizontal bar)
- Average vs Upside scatter
- Season Trends line (single selected player)

Charts and Rankings remember key control selections for the current browser session (for example, chart view, position, selected stat, trend player, and ranking weights) via `sessionStorage`. Individual chart views are loaded on demand from the charts feature folder rather than bundled into one large feature entry chunk.

Schedules and Depth Charts share the same team navigation pattern via [`src/features/teams/TeamBrowser.jsx`](src/features/teams/TeamBrowser.jsx):

- Division Browser
- Team Search

## Key Source Paths

| Area                        | File/Folder                                                                                                                                                                                                                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API wrapper                 | [`src/api/index.js`](src/api/index.js)                                                                                                                                                                                                                                                             |
| App shell                   | [`src/app/App.jsx`](src/app/App.jsx), [`src/app/App.css`](src/app/App.css), [`src/app/shell/`](src/app/shell)                                                                                                                                                                                      |
| Shared brand styles         | [`src/app/brand/content.js`](src/app/brand/content.js), [`src/app/brand/brand.css`](src/app/brand/brand.css)                                                                                                                                                                                       |
| Shared UI                   | [`src/shared/ui/`](src/shared/ui)                                                                                                                                                                                                                                                                  |
| Shared hooks                | [`src/shared/hooks/`](src/shared/hooks)                                                                                                                                                                                                                                                            |
| Shared utilities            | [`src/shared/utils/`](src/shared/utils)                                                                                                                                                                                                                                                            |
| Home feature                | [`src/features/home/`](src/features/home)                                                                                                                                                                                                                                                          |
| Statistics feature          | [`src/features/statistics/`](src/features/statistics)                                                                                                                                                                                                                                              |
| Charts feature              | [`src/features/statistics/charts/`](src/features/statistics/charts)                                                                                                                                                                                                                                |
| Rankings feature            | [`src/features/statistics/rankings/`](src/features/statistics/rankings)                                                                                                                                                                                                                            |
| Comparison feature          | [`src/features/statistics/comparison/`](src/features/statistics/comparison)                                                                                                                                                                                                                        |
| Player search feature       | [`src/features/statistics/player-search/`](src/features/statistics/player-search)                                                                                                                                                                                                                  |
| Shared player modal flow    | [`src/app/App.jsx`](src/app/App.jsx), [`src/features/statistics/player-details/usePlayerDetails.js`](src/features/statistics/player-details/usePlayerDetails.js), [`src/features/statistics/player-details/PlayerDetailsModal.jsx`](src/features/statistics/player-details/PlayerDetailsModal.jsx) |
| Player modal sub-components | [`src/features/statistics/player-details/`](src/features/statistics/player-details)                                                                                                                                                                                                                |
| Team browser feature        | [`src/features/teams/`](src/features/teams)                                                                                                                                                                                                                                                        |
| Feature config              | [`src/features/statistics/statisticsOptions.js`](src/features/statistics/statisticsOptions.js), [`src/features/statistics/charts/ChartsMeta.js`](src/features/statistics/charts/ChartsMeta.js), [`src/shared/utils/statMeta.js`](src/shared/utils/statMeta.js)                                     |
| Tests                       | [`tests/app/`](tests/app), [`tests/features/`](tests/features), [`tests/shared/`](tests/shared), [`tests/support/setup.js`](tests/support/setup.js)                                                                                                                                                |
| Global styles/tokens        | [`src/index.css`](src/index.css)                                                                                                                                                                                                                                                                   |

## Build

```bash
npm run build
npm run preview
```
