import axios from 'axios';

const API_URL = "https://spurtive-subtilely-earl.ngrok-free.dev";

export function fetchInsights(token) {
  return axios.get(`${API_BASE}/insights/analyze?token=${token}`);
}