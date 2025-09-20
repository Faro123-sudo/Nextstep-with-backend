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

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default Route: Redirect "/" based on login state */}
        <Route
          path="/"
          element={
            getAccessToken() ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Route */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Fallback for unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
