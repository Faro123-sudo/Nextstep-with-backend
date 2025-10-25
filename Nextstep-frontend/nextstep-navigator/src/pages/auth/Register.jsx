import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, login } from "../../utils/auth";
import { useProfile } from "../../context/ProfileContext"; // Import the profile hook
import Lottie from "lottie-react";
import Logo from "../../assets/logo.webp";
import { User, Mail, Lock, Briefcase, AlertCircle } from "lucide-react"; // Import icons
import animationData from "../../assets/animation/looking.json";
import "bootstrap/dist/css/bootstrap.min.css";
import "../../components/staticFiles/LandingPage.css";

const Register = () => {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { setProfile } = useProfile(); // Get the setProfile function from context

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    if (!firstName || !lastName || !username || !email || !password || !confirmPassword || !role) {
      setError("All fields are required");
      return;
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await register(firstName, lastName, username, email, password, confirmPassword, role);
      await login(username, password, setProfile); // Pass setProfile to login
      navigate("/"); // Navigate to the home page
    } catch (err) {
      if (err.response?.data) {
        const errorData = err.response.data;
        const errorMessages = Object.values(errorData).flat(); // Get all error messages
        setError(errorMessages[0] || "Registration failed."); // Display the first error
      } else {
        setError("Registration failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center landing-bg" style={{ paddingTop: '0px !important;' }}>
        <div className="container">
          <div className="row text-center mb-3">
            <div className="col-12" data-aos="fade-up" data-aos-delay="300">
              <img 
                src={Logo} 
                alt="NextStep Navigator Logo" 
                className="mb-4 fade-in" 
                style={{ height: '70px' }}
              />
              <h1 className="display-3 fw-bold text-primary mb-3">
                NextStep Navigator
              </h1>
              <h2 className="fw-semibold text-secondary mb-2">
                Your Guide to the Future
              </h2>
            </div>
          </div>
          <div className="row justify-content-center align-items-center">
            <div className="col-md-6 col-lg-5 text-center mb-5 mb-md-0" data-aos="fade-right" data-aos-delay="500">
              <Lottie
                animationData={animationData}
                loop={true}
                style={{ width: "100%", maxWidth: "400px", margin: "auto" }}
              />
              <p className="lead mt-4 text-muted px-3">
                Discover your perfect career path with personalized guidance and insights tailored just for you.
              </p>
            </div>
            <div className="col-md-6 col-lg-5 mb-2" data-aos="fade-left" data-aos-delay="500">
              <div className="form-container p-4 p-md-5 shadow-lg rounded-3">
                <form onSubmit={handleRegister} className="d-grid gap-3">
                  <h4 className="fw-bold mb-2 text-center">Create Your Account</h4>
                  <div className="form-group">
                    <User className="form-icon" size={18} />
                    <input
                      type="text"
                      className="form-control"
                      placeholder="First Name"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <User className="form-icon" size={18} />
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Last Name"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <User className="form-icon" size={18} />
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <Mail className="form-icon" size={18} />
                    <input
                      type="email"
                      className="form-control"
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <Briefcase className="form-icon" size={18} />
                    <select
                      className="form-control"
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      required
                    >
                      <option value="" disabled>Select Role</option>
                      <option value="student">Student</option>
                      <option value="graduate">Graduate</option>
                      <option value="professional">Professional</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <Lock className="form-icon" size={18} />
                    <input
                      type={showPassword ? "text" : "password"}
                      className="form-control"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <Lock className="form-icon" size={18} />
                    <input
                      type={showPassword ? "text" : "password"}
                      className="form-control"
                      placeholder="Confirm Password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
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
                  {error && (
                    <div className="alert alert-danger p-2 form-error-alert" role="alert">
                      <AlertCircle size={18} /> {error}
                    </div>
                  )}
                  <button
                    type="submit"
                    className="btn btn-primary btn-lg w-100 py-2 fw-bold rounded-pill"
                    disabled={loading}
                  >
                    {loading ? "Registering..." : "Register"}
                  </button>
                </form>
                <p className="text-center mt-3">
                  Already have an account?{" "}
                  <Link to="/login" className="link-primary">
                    Login
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Register;
