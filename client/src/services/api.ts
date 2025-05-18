// src/api/axios.ts
import type { AuthResponse } from '@/types/auth';
import axios from 'axios';

const BASE_API_URL = 'http://localhost:8000/api/v1';

let accessToken = ''; // Store in memory

export const setAccessToken = (token: string) => {
  accessToken = token;
};

export const api = axios.create({
  baseURL: BASE_API_URL,
  withCredentials: true, // So cookies (refresh token) are sent
});

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const originalRequest = err.config;

    // Avoid infinite loop
    console.log('err', err.response?.status, originalRequest);
    if (err.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const res = await axios.post<AuthResponse>(`${BASE_API_URL}/auth/refresh`);

        setAccessToken(res.data.access_token);
        originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;

        return api(originalRequest);
      } catch (refreshErr) {
        return Promise.reject(refreshErr);
      }
    }
    return Promise.reject(err);
  }
);
