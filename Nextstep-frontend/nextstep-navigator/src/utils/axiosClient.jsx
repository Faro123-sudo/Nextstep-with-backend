import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth";

// Create a .env file in the root of the nextstep-navigator directory and add the following line:
// VITE_API_URL=http://localhost:8000/api

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  // send credentials (cookies) for cross-origin requests so HttpOnly refresh cookie is accepted
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Single-flight refresh helper so simultaneous 401s wait for one refresh call
let refreshPromise = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {};

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // If a refresh is already in progress, wait for it
      if (refreshPromise) {
        try {
          const newAccess = await refreshPromise;
          if (newAccess) {
            originalRequest.headers = originalRequest.headers || {};
            originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
            return api(originalRequest);
          }
        } catch (e) {
          // fall through to attempt refresh ourselves
        }
      }

      // Start a refresh attempt (single-flight)
      refreshPromise = (async () => {
        // First try stored refresh token
        const storedRefresh = getRefreshToken();
        if (storedRefresh) {
          try {
            // Try the backend's refresh endpoint; accept both /auth/refresh/ and /auth/token/refresh/ depending on server config
            let response;
            try {
              response = await axios.post(`${import.meta.env.VITE_API_URL || "http://localhost:8000/api"}/auth/refresh/`, { refresh: storedRefresh });
            } catch (e) {
              response = await axios.post(`${import.meta.env.VITE_API_URL || "http://localhost:8000/api"}/auth/token/refresh/`, { refresh: storedRefresh });
            }
            const newAccess = response.data.access || response.data.access_token;
            setTokens(newAccess, response.data.refresh || storedRefresh);
            return newAccess;
          } catch (err) {
            console.warn("Stored refresh failed, will try cookie-based refresh", err.message || err);
          }
        }

        // Fallback: cookie-based refresh
        try {
          const refreshUrl = `${import.meta.env.VITE_API_URL || "http://localhost:8000/api"}/auth/refresh/`;
          const response = await axios.post(refreshUrl, null, { withCredentials: true });
          const newAccess = response.data.access;
          setTokens(newAccess, null);
          return newAccess;
        } catch (refreshError) {
          console.error("Cookie-based token refresh failed:", refreshError);
          // Clear tokens and return null so callers know refresh failed
          clearTokens();
          return null;
        }
      })();

      try {
        const newAccess = await refreshPromise;
        refreshPromise = null;
        if (newAccess) {
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
          return api(originalRequest);
        }
        // If refresh failed, let the caller handle redirect; avoid forcing navigation here to prevent reload loops
        return Promise.reject(error);
      } catch (e) {
        refreshPromise = null;
        return Promise.reject(e);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
