import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, isAuthenticated }) {
  if (!isAuthenticated) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to. This allows us to send them along to that page after they
    // log in.
    return <Navigate to="/login" replace />;
  }

  return children;
}
