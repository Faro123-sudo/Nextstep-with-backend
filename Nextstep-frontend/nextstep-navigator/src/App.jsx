// import { BrowserRouter as Router } from "react-router-dom";
// import DisplayPages from "./components/DisplayPages";
// import LandingPage from "./components/LandingPage";
// import { useState, useEffect } from "react";
// import AOS from "aos";
// import "aos/dist/aos.css";

// function App() {
//   const [isAuthenticated, setIsAuthenticated] = useState(false);

//   useEffect(() => {
//     AOS.init({ duration: 1000, once: true });

//     const username = sessionStorage.getItem("username");
//     if (username) setIsAuthenticated(true);
//   }, []);

//   return (
//     <Router>
//       {isAuthenticated ? (
//         <DisplayPages />
//       ) : (
//         <LandingPage onNavigate={() => setIsAuthenticated(true)} />
//       )}
//     </Router>
//   );
// }

// export default App;




import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./api_testing/Login";
import Register from "./api_testing/Register";
import Dashboard from "./api_testing/Dashboard";
import ProtectedRoute from "./api_testing/ProtectedRoute";
import { getAccessToken } from "./utils/auth";
import DisplayPages from "./components/DisplayPages";
import AOS from "aos";
import "aos/dist/aos.css";
import { useEffect } from "react";
import { useAutoRefresh } from "./hooks/useAutoRefresh";

export default function App() {
  useAutoRefresh();
  useEffect(() => {
    AOS.init({ duration: 1000, once: true });
  }, []);

  const isAuthenticated = getAccessToken();

  return (
    <BrowserRouter>
      <Routes>
        {/* Root Redirect */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <DisplayPages replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Auth Routes */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/" /> : <Register />}
        />

        {/* Protected Dashboard */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DisplayPages />
            </ProtectedRoute>
          }
        />

        {/* Catch-All */}
        <Route
          path="*"
          element={
            isAuthenticated ? (
              <DisplayPages/>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
