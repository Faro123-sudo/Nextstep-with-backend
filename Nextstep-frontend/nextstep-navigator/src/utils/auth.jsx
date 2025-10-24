import api from "./axiosClient";

// ---------- TOKEN MANAGEMENT ----------

export const getAccessToken = () => localStorage.getItem("access_token");
export const getRefreshToken = () => localStorage.getItem("refresh_token");

export const setTokens = (access, refresh) => {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
};

export const clearTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

// ---------- AUTH FUNCTIONS ----------

// Login and store tokens
export const login = async (email, password) => {
  const response = await api.post("/auth/login/", { email, password });
  // Backend sets refresh token as HttpOnly cookie and returns the access token in the body
  const access = response.data.access || response.data.access_token || response.data.accessToken;
  const refresh = response.data.refresh || null;
  setTokens(access, refresh);
  return response.data;
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
  return await api.post("/auth/register/", {
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
export const logout = async () => {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    try {
      await api.post("/auth/logout/", { refresh: refreshToken });
    } catch (error) {
      console.error("Logout API call failed:", error);
    }
  }
  clearTokens();
};

// Send password reset email
export const sendPasswordResetEmail = async (email) => {
    try {
        const response = await api.post("/auth/password/reset/", { email });
        return response.data; // Return the success message/data
    } catch (error) {
        // Log the error for debugging
        console.error("Password reset request failed:", error.response?.data || error.message);
        // Throw the error so the component can catch and display it
        throw error; 
    }
};

// Confirm and set the new password
export const resetPasswordConfirm = async (uid, token, password, confirmPassword) => {
  return await api.post("/auth/password/reset/confirm/", {
    uidb64: uid,
    token: token,
    new_password: password,
    confirm_new_password: confirmPassword,
  });
};
