import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/auth"; // adjust if needed

// ---------- TOKEN STORAGE ----------
const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

// Save tokens to localStorage
export const saveTokens = (access, refresh) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
};

// Get tokens
export const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);

// Remove tokens
export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// ---------- AUTH FUNCTIONS ----------

// Login and store tokens
export const login = async (username, password, onLoginSuccess) => {
  const response = await axios.post(`${API_URL}/login/`, { username, password });
  saveTokens(response.data.access, response.data.refresh);
  onLoginSuccess(); // Callback to update app state
  return response.data; // Return data for local component use if needed
};

// Register new user
export const register = async (
  firstName,
  lastName,
  username,
  email,
  password,
  confirmPassword,
  role
) => {
  return await axios.post(`${API_URL}/register/`, {
    first_name: firstName,
    last_name: lastName,
    username,
    email,
    password,
    password2: confirmPassword,
    role,
  });
};

// Logout user
export const logout = async (onLogoutSuccess) => {
  const refreshToken = getRefreshToken();

  if (refreshToken) {
    try {
      // Call the backend to blacklist the refresh token
      // This endpoint requires authentication, so we must pass the access token.
      await axios.post(`${API_URL}/logout/`, {
        refresh: refreshToken,
      }, {
        headers: { Authorization: `Bearer ${getAccessToken()}` }
      }
      );
    } catch (error) {
      // Log the error but proceed with local cleanup
      console.error("Logout API call failed:", error);
    }
  }
  // Always clear tokens from local storage
  clearTokens();
  onLogoutSuccess(); // Callback to update app state
};

// Fetch logged-in user's profile
export const getProfile = async () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/profile/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch profile", error);
    return null;
  }
};


// Refresh token if access token is expired
export const refreshAccessToken = async () => {
  const refresh = getRefreshToken();
  if (!refresh) {
    logout();
    return;
  }
  try {
    const response = await axios.post(`${API_URL}/token/refresh/`, {
      refresh,
    });
    saveTokens(response.data.access, refresh);
    return response.data.access;
  } catch (err) {
    console.error("Failed to refresh token", err);
    logout();
  }
};

// Setup axios interceptor to auto-refresh token
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newAccess = await refreshAccessToken();
      if (newAccess) {
        originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
        return axios(originalRequest);
      }
    }
    return Promise.reject(error);
  }
);

// Send password reset email
export const sendPasswordResetEmail = async (email) => {
  return await axios.post(`${API_URL}/password/reset/`, { email });
};
