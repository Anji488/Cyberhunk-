import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export function fetchInsights(token) {
  return axios.get(`${API_BASE}/insights/analyze?token=${token}`);
}