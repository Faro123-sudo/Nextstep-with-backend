// src/utils/auth.js
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/auth";

export const login = async (username, password) => {
  const res = await axios.post(`${API_URL}/login/`, { username, password });
  localStorage.setItem("access", res.data.access);
  localStorage.setItem("refresh", res.data.refresh);
  return res.data;
};

// Updated register function to include firstName and lastName
export const register = async (firstName, lastName, username, email, password, password2, role) => {
  return await axios.post(`${API_URL}/register/`, {
    first_name: firstName,
    last_name: lastName,
    username,
    email,
    password,
    password2,
    role 
  });
};

export const logout = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

export const getAccessToken = () => localStorage.getItem("access");
export const getRefreshToken = () => localStorage.getItem("refresh");

// Fetch user profile
export const getProfile = async () => {
  const token = getAccessToken();
  if (!token) return null;

  const res = await axios.get(`${API_URL}/profile/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  return res.data; // user object
};