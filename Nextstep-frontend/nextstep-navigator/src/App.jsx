
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import AOS from "aos";
import "aos/dist/aos.css";

// Your custom components and utilities
import Login from "./api_testing/Login";
import Register from "./api_testing/Register";
import ForgotPassword from "./api_testing/ForgotPassword";
import ProtectedRoute from "./api_testing/ProtectedRoute";
import DisplayPages from "./components/DisplayPages";
import { getAccessToken, logout } from "./utils/auth";
import { useAutoRefresh } from "./hooks/useAutoRefresh";
import { ProfileProvider } from "./context/ProfileContext"; // Import ProfileProvider

export default function App() {
  // 1. Initialize state based on the presence of an access token
  const [isAuthenticated, setIsAuthenticated] = useState(!!getAccessToken());

  // 2. Custom hook for handling proactive token monitoring/refresh
  useAutoRefresh();

  useEffect(() => {
    // Initialize AOS for animations
    AOS.init({ duration: 1000, once: true });

    // 3. Keep UI in sync if auth token changes in another tab (e.g., user logs in elsewhere)
    const handleStorageChange = () => {
      // Update state if localStorage changes
      setIsAuthenticated(!!getAccessToken());
    };

    window.addEventListener("storage", handleStorageChange);

    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  // Handler to wrap logout and state update cleanly
  const handleLogout = () => {
    // Calls logout utility, which then updates isAuthenticated state via callback
    logout(() => setIsAuthenticated(false));
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* --- Public Routes --- */}
        <Route
          path="/login"
          // If already authenticated, redirect to the main app area
          element={isAuthenticated ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />}
        />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* --- Protected Route --- */}
        <Route
          path="/*"
          element={
            // The ProtectedRoute component ensures the inner element is only rendered if authenticated
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              {/* Wrap DisplayPages with ProfileProvider.
                  This makes the profile data available via context to all child components (Header, DisplayPages content)
                  and ensures getProfile() is called only once per authenticated session.
                */}
              <ProfileProvider>
                <DisplayPages onLogout={handleLogout} />
              </ProfileProvider>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}