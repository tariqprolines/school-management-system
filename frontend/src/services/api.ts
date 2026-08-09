import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const API_ACCESS_TOKEN = import.meta.env.VITE_API_ACCESS_TOKEN || 'dev-api-access-token';

export interface ApiResponse<T = unknown> {
  status_code: number;
  status: 'success' | 'error';
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  page: number;
  per_page: number;
  total_records: number;
  data: T[];
}

const getAuthToken = (): string | null => {
  try {
    const userData = localStorage.getItem('user');
    if (userData) {
      return JSON.parse(userData)?.token || null;
    }
  } catch {
    return null;
  }
  return null;
};

export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-Access-Token': API_ACCESS_TOKEN,
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAuthToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse>) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      if (!url.includes('/login')) {
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
