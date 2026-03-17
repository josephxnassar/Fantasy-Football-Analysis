// API client for the Fantasy Football backend.

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({ baseURL: API_BASE_URL, timeout: 15_000, headers: { 'Content-Type': 'application/json' } });

export const getPlayer = (playerName, season = null) => {
  return api.get(`/player/${encodeURIComponent(playerName)}`, { params: season ? { season } : {} });
};

export const searchPlayers = (query, position = null) => {
  return api.get('/search', { params: { q: query, ...(position && { position }) } });
};

export const getDivisions = () => {
  return api.get('/teams/divisions');
};

export const getTeamSchedule = (team, season = null) => {
  return api.get(`/schedules/${encodeURIComponent(team)}`, { params: season ? { season } : {} });
};

export const getTeamDepthChart = (team) => {
  return api.get(`/depth-charts/${encodeURIComponent(team)}`);
};

export const getChartData = (position, season = null) => {
  return api.get('/chart-data', { params: { position, ...(season && { season }) } });
};

export const getConsistencyData = (position, season = null, topN = 40) => {
  return api.get('/consistency-data', { params: { position, top_n: topN, ...(season && { season }) } });
};

export const getPlayerTrendData = (playerName, position, stat) => {
  return api.get('/player-trend', { params: { player_name: playerName, position, stat } });
};

export const getAppInfo = () => {
  return api.get('/app-info');
};
