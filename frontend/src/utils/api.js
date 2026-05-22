// src/utils/api.js
import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  withCredentials: true, // Include cookies for refresh token
});

let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

export const getAccessToken = () => {
  return accessToken;
};

// Request interceptor to add JWT token
client.interceptors.request.use(
  (config) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { data } = await axios.post(
          "/api/auth/refresh",
          {},
          { withCredentials: true }
        );

        accessToken = data.accessToken;
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;

        return client(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        accessToken = null;
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

const api = {
  get: async (url, config) => {
    const res = await client.get(url, config);
    return res.data;
  },
  post: async (url, body, config) => {
    const res = await client.post(url, body, config);
    return res.data;
  },
};

export default api;
