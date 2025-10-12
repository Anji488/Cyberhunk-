import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export function fetchInsights(token) {
  return axios.get(`${API_BASE}/insights/analyze?token=${token}`);
}