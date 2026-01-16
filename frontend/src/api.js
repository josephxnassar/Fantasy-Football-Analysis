import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getRankings = (format = 'redraft', position = null, model = 'ridge') => {
  return api.get('/rankings', {
    params: { format, position, model },
  });
};

export const getPlayer = (playerName) => {
  return api.get(`/player/${playerName}`);
};

export const getSchedule = (team) => {
  return api.get(`/schedule/${team}`);
};

export const searchPlayers = (query, position = null) => {
  return api.get('/search', {
    params: { q: query, position },
  });
};

export const getStreamingRecommendations = (position, week = 1) => {
  return api.get(`/streaming/${position}/${week}`);
};

export default api;
