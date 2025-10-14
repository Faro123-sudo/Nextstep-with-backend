import { Navigate } from "react-router-dom";

// A simple loading spinner component (or you can use a more complex one)
const LoadingSpinner = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    Loading...
  </div>
);

export default function ProtectedRoute({ children, profile, loading }) {
  if (loading) {
    // While checking for the profile, show a loading indicator.
    // This prevents a flash of the login page before the user is authenticated.
    return <LoadingSpinner />;
  }

  if (!profile) {
    // If not loading and there's no profile, redirect to login.
    return <Navigate to="/login" replace />;
  }

  // If the profile exists, render the protected content.
  return children;
}