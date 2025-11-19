import axios from 'axios';

const API_BASE = "https://cyberhunk.onrender.com";

export function fetchInsights(token) {
  return axios.get(`${API_BASE}/insights/analyze?token=${token}`);
}