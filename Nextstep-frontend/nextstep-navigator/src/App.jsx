// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./api_testing/Login";
import Register from "./api_testing/Register";
import DisplayPages from "./components/DisplayPages";
import ProtectedRoute from "./api_testing/ProtectedRoute";
import { getAccessToken, logout } from "./utils/auth";
import AOS from "aos";
import "aos/dist/aos.css";
import { useEffect, useState } from "react";
import { useAutoRefresh } from "./hooks/useAutoRefresh";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!getAccessToken());
  useAutoRefresh();

  useEffect(() => {
    AOS.init({ duration: 1000, once: true });

    // keep UI in sync if auth token changes in another tab
    const handleStorageChange = () => setIsAuthenticated(!!getAccessToken());
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login onLogin={() => setIsAuthenticated(true)} />}
        />
        <Route path="/register" element={<Register />} />

        <Route
          path="/*"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <DisplayPages onLogout={() => logout(() => setIsAuthenticated(false))} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
