// src/utils/auth.js
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/auth";

export const login = async (username, password) => {
  const res = await axios.post(`${API_URL}/login/`, { username, password });
  localStorage.setItem("access", res.data.access);
  localStorage.setItem("refresh", res.data.refresh);
  return res.data;
};

export const register = async (username, password, email) => {
  return await axios.post(`${API_URL}/register/`, { username, password, email });
};

export const logout = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

export const getAccessToken = () => localStorage.getItem("access");
export const getRefreshToken = () => localStorage.getItem("refresh");

// NEW: Fetch user profile
export const getProfile = async () => {
  const token = getAccessToken();
  if (!token) return null;

  const res = await axios.get(`${API_URL}/profile/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  return res.data; // user object
};
