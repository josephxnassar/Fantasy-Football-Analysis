/* API client for Fantasy Football backend */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch player details
 * @param {string} playerName - Player name
 * @param {number|null} season - Season year or null for career average
 */
export const getPlayer = (playerName, season = null) => {
  return api.get(`/player/${encodeURIComponent(playerName)}`, {
    params: season ? { season } : {},
  });
};

/**
 * Search for players
 * @param {string} query - Search query
 * @param {string|null} position - Position filter or null for all
 */
export const searchPlayers = (query, position = null) => {
  return api.get('/search', {
    params: { q: query, ...(position && { position }) },
  });
};

/**
 * Fetch NFL division structure
 * @returns Division hierarchy and team names
 */
export const getDivisions = () => {
  return api.get('/teams/divisions');
};

/**
 * Fetch team schedule
 * @param {string} team - Team abbreviation (e.g., "KC")
 * @param {number|null} season - Season year or null for most recent available
 */
export const getTeamSchedule = (team, season = null) => {
  return api.get(`/schedules/${encodeURIComponent(team)}`, {
    params: season ? { season } : {},
  });
};

/**
 * Fetch depth chart for a specific team
 * @param {string} team - Team abbreviation (e.g., "KC")
 */
export const getTeamDepthChart = (team) => {
  return api.get(`/depth-charts/${encodeURIComponent(team)}`);
};

/**
 * Fetch chart data for bar charts
 * @param {string} position - Position filter (QB, RB, WR, TE)
 * @param {number|null} season - Season year or null for most recent
 */
export const getChartData = (position, season = null) => {
  return api.get('/chart-data', {
    params: { position, ...(season && { season }) },
  });
};

/**
 * Fetch weekly consistency/upside chart data.
 * @param {string} position - Position filter (QB, RB, WR, TE, Overall)
 * @param {number|null} season - Season year or null for most recent
 * @param {number} topN - Number of top seasonal players to evaluate
 */
export const getConsistencyData = (position, season = null, topN = 40) => {
  return api.get('/consistency-data', {
    params: { position, top_n: topN, ...(season && { season }) },
  });
};

/**
 * Fetch season trend points for one player/stat.
 * @param {string} playerName - Player name
 * @param {string} position - Position scope (QB, RB, WR, TE, Overall)
 * @param {string} stat - Stat key/column
 */
export const getPlayerTrendData = (playerName, position, stat) => {
  return api.get('/player-trend', {
    params: { player_name: playerName, position, stat },
  });
};

/**
 * Fetch application overview metadata
 * @returns Seasons, player counts, game logs, rookie count, and stat column count
 */
export const getAppInfo = () => {
  return api.get('/app-info');
};
