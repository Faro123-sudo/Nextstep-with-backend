import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../../utils/auth";
import { useProfile } from "../../context/ProfileContext"; // Import the profile hook
import Lottie from "lottie-react";
import Logo from "../../assets/logo.webp";
import animationData from "../../assets/animation/looking.json";
import "bootstrap/dist/css/bootstrap.min.css";
import "../../components/staticFiles/LandingPage.css";

const Login = () => {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { refreshProfile } = useProfile(); // Get the refreshProfile function from context

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!emailOrUsername || !password) {
      setError("Please fill in all fields");
      return;
    }

    try {
      setLoading(true);
      setError("");
      // Pass setProfile to the login function to update state immediately
      await login(emailOrUsername, password);
      await refreshProfile(); // Manually refresh the profile
      navigate("/");
    } catch (err) {
      const errorMessage = err.response?.data?.detail || "Login failed. Please check your credentials.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center landing-bg">
      <div className="container">
        <div className="row text-center mb-5">
          <div className="col-12" data-aos="fade-up" data-aos-delay="300">
            <img 
              src={Logo} 
              alt="NextStep Navigator Logo" 
              className="mb-4 fade-in" 
              style={{ height: "70px" }}
            />
            <h1 className="display-3 fw-bold text-primary mb-3">
              NextStep Navigator
            </h1>
            <h2 className="fw-semibold text-secondary mb-4">
              Your Guide to the Future
            </h2>
          </div>
        </div>
        <div className="row justify-content-center align-items-center">
          <div className="col-md-6 col-lg-5 text-center mb-5 mb-md-0" data-aos="fade-right" data-aos-delay="500">
            <Lottie animationData={animationData} loop style={{ width: "100%", maxWidth: "400px", margin: "auto" }} />
            <p className="lead mt-4 text-muted px-3">
              Discover your perfect career path with personalized guidance and insights tailored just for you.
            </p>
          </div>
          <div className="col-md-6 col-lg-5" data-aos="fade-left" data-aos-delay="500">
            <div className="form-container p-4 p-md-5 shadow-lg rounded-3">
              <form onSubmit={handleLogin} className="d-grid gap-3">
                <h4 className="fw-bold mb-4 text-center">Login to Your Account</h4>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Email or Username"
                  value={emailOrUsername}
                  onChange={(e) => setEmailOrUsername(e.target.value)}
                  required
                />
                <input
                  type={showPassword ? "text" : "password"}
                  className="form-control"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <div className="d-flex justify-content-between align-items-center">
                  <div className="form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="showPasswordCheck"
                      checked={showPassword}
                      onChange={() => setShowPassword(!showPassword)}
                    />
                    <label className="form-check-label" htmlFor="showPasswordCheck">
                      Show Password
                    </label>
                  </div>
                  <Link to="/forgot-password" className="link-primary small">
                    Forgot Password?
                  </Link>
                </div>
                {error && <p className="text-danger text-sm">{error}</p>}
                <button
                  type="submit"
                  className="btn btn-primary btn-lg w-100 py-2 fw-bold rounded-pill"
                  disabled={loading}
                >
                  {loading ? "Logging in..." : "Login"}
                </button>
              </form>
              <p className="text-center mt-3">
                Don’t have an account?{" "}
                <Link to="/register" className="link-primary">
                  Register
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;