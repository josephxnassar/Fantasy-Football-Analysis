# Frontend

Last verified: 2026-02-19

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](package.json)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](vite.config.js)
[![Axios](https://img.shields.io/badge/Axios-HTTP-5A29E4)](src/api.js)
[![Recharts](https://img.shields.io/badge/Recharts-Charts-22C55E)](src/components/Charts.jsx)

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
npm run build
```

## Environment And Proxy

- API base override: `VITE_API_URL` (default `http://localhost:8000/api`)
- Dev proxy config: [`vite.config.js`](vite.config.js)
  - `/api` -> `http://localhost:8000`

## UI Navigation Model

Top-level tabs in [`src/App.jsx`](src/App.jsx):
- `Statistics`
- `Schedules`
- `Depth Charts`

Statistics sub-tabs in [`src/components/Statistics.jsx`](src/components/Statistics.jsx):
- Charts
- Player Search

Schedules and Depth Charts share the same team navigation pattern via [`src/components/TeamBrowser.jsx`](src/components/TeamBrowser.jsx):
- Division Browser
- Team Search

## Key Source Paths

| Area | File/Folder |
|---|---|
| API wrapper | [`src/api.js`](src/api.js) |
| Hooks | [`src/hooks/`](src/hooks) |
| Feature components | [`src/components/`](src/components) |
| Reusable components | [`src/components/common/`](src/components/common) |
| Player modal sub-components | [`src/components/player-details/`](src/components/player-details) |
| Utilities | [`src/utils/`](src/utils) |
| Global styles/tokens | [`src/index.css`](src/index.css) |

## Build

```bash
npm run build
npm run preview
```
