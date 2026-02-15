/**
 * API client for Fantasy Football backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch player rankings
 * @param {string} format - 'redraft' or 'dynasty'
 * @param {string|null} position - Position filter or null for all
 */
export const getRankings = (format = 'redraft', position = null) => {
  return api.get('/rankings', {
    params: { format, position },
  });
};

/**
 * Fetch player details
 * @param {string} playerName - Player name
 * @param {number|null} season - Season year or null for career average
 */
export const getPlayer = (playerName, season = null) => {
  return api.get(`/player/${playerName}`, {
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
    params: { q: query, position },
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
  return api.get(`/schedules/${team}`, {
    params: season ? { season } : {},
  });
};

/**
 * Fetch depth chart for a specific team
 * @param {string} team - Team abbreviation (e.g., "KC")
 */
export const getTeamDepthChart = (team) => {
  return api.get(`/depth-charts/${team}`);
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

export default api;
