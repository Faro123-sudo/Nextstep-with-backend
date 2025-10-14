
import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import AOS from "aos";
import "aos/dist/aos.css";

// Your custom components and utilities
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPasswordConfirm from "./pages/auth/ResetPasswordConfirm";
import ProtectedRoute from "./pages/auth/ProtectedRoute";
import DisplayPages from "./components/DisplayPages";
import { logout } from "./utils/auth";
import { ProfileProvider, useProfile } from "./context/ProfileContext";
import ToastMessage from "./components/ToastMessage";

// A new component to handle the main application logic
function AppContent() {
  const { profile, loading, setProfile } = useProfile();
  const navigate = useNavigate();
  const [toast, setToast] = React.useState({ show: false, message: '', variant: 'success' });

  // Handler to wrap logout and state update cleanly
  const handleLogout = async () => {
    await logout(); // This now just calls the API
    // Clear profile in context so protected UI updates immediately
    try {
      setProfile(null);
    } catch (e) {
      // ignore if not available
    }
    setToast({ show: true, message: 'Logged out successfully', variant: 'success' });
    navigate("/login", { replace: true }); // Redirect after logout
  };

  // This is the core of the protected routing logic now
  return (
    <>
      <Routes>
      <Route path="/login" element={profile ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/register" element={profile ? <Navigate to="/" replace /> : <Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password-confirm" element={<ResetPasswordConfirm />} />

      <Route
        path="/*"
        element={
          <ProtectedRoute profile={profile} loading={loading}>
            <DisplayPages onLogout={handleLogout} />
          </ProtectedRoute>
        }
      />
    </Routes>
      <ToastMessage show={toast.show} message={toast.message} variant={toast.variant} onClose={() => setToast({ ...toast, show: false })} />
    </>
  );
}

export default function App() {
  useEffect(() => {
    // Initialize AOS for animations
    AOS.init({ duration: 1000, once: true });
  }, []);

  return (
    <BrowserRouter>
      <ProfileProvider>
        <AppContent />
      </ProfileProvider>
    </BrowserRouter>
  );
}