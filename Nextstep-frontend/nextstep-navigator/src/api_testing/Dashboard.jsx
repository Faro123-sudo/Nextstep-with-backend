import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getProfile, logout } from "../utils/auth";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const profile = await getProfile();
        setUser(profile);
      } catch (err) {
        console.error("Failed to fetch profile:", err);
        logout();
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [navigate]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center vh-100">
        <p className="fs-5 fw-semibold">Loading dashboard...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="d-flex align-items-center justify-content-center vh-100">
        <p className="text-danger fw-semibold">
          Could not load profile. Please log in again.
        </p>
      </div>
    );
  }

  return (
    <div className="container d-flex flex-column align-items-center justify-content-center vh-100 text-center">
      <h1 className="display-4 fw-bold mb-4">
        Welcome, <span className="text-primary">{user.username}</span> 🎉
      </h1>
      {user.email && <p className="text-secondary">Email: {user.email}</p>}
      {user.role && <p className="text-secondary">Role: {user.role}</p>}


      <button
        onClick={handleLogout}
        className="btn btn-danger mt-4"
      >
        Logout
      </button>
    </div>
  );
}