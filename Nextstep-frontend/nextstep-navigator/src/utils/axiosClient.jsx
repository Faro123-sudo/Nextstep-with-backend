import axios from "axios";
import { getAccessToken, refreshToken, clearTokens } from "./auth";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle expired access token (401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const newAccess = await refreshToken();
        if (newAccess) {
          error.config.headers.Authorization = `Bearer ${newAccess}`;
          return api(error.config); // retry original request
        }
      } catch (refreshErr) {
        clearTokens();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
