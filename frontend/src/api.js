import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
});

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('wa_token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('wa_token');
      window.location.href = '/giris';
    }
    return Promise.reject(err);
  }
);

export default api;
