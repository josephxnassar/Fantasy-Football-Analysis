import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getRankings = (format = 'redraft', position = null) => {
  return api.get('/rankings', {
    params: { format, position },
  });
};

export const getPlayer = (playerName, season = null) => {
  return api.get(`/player/${playerName}`, {
    params: season ? { season } : {},
  });
};

export const searchPlayers = (query, position = null) => {
  return api.get('/search', {
    params: { q: query, position },
  });
};

export default api;
