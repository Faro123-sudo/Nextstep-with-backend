import React from "react";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { sendPasswordResetEmail } from "../../utils/auth";
import Lottie from "lottie-react";
import { Mail, AlertCircle, CheckCircle } from "lucide-react";
import Logo from "../../assets/logo.webp";
import animationData from "../../assets/animation/forgot-password.json";
import "bootstrap/dist/css/bootstrap.min.css";
import "../../components/staticFiles/LandingPage.css";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError("Please enter your email");
      return;
    }
    try {
      setLoading(true);
      setError("");
      setMessage("");
      await sendPasswordResetEmail(email);
      setMessage("If an account with that email exists, a password reset link has been sent.");
    } catch (err) {
      const errorMessage = err.response?.data?.detail || "Failed to send reset email. Please try again.";
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
            <img src={Logo} alt="NextStep Navigator Logo" className="mb-4 fade-in" style={{ height: "70px" }} />
            <h1 className="display-3 fw-bold text-primary mb-3">NextStep Navigator</h1>
            <h2 className="fw-semibold text-secondary mb-4">Your Guide to the Future</h2>
          </div>
        </div>
        <div className="row justify-content-center align-items-center mb-5">
          <div className="col-md-6 col-lg-5 text-center mb-5 mb-md-0" data-aos="fade-right" data-aos-delay="500">
            <Lottie animationData={animationData} loop style={{ width: "100%", maxWidth: "400px", margin: "auto" }} />
            <p className="lead mt-4 text-muted px-3">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>
          <div className="col-md-6 col-lg-5" data-aos="fade-left" data-aos-delay="500">
            <div className="form-container p-4 p-md-5 shadow-lg rounded-3">
              <form onSubmit={handleSubmit} className="d-grid gap-3">
                <h4 className="fw-bold mb-4 text-center">Reset Your Password</h4>
                <div className="form-group">
                  <Mail className="form-icon" size={18} />
                  <input
                      type="email"
                      className="form-control"
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={!!message} // Disable input after success
                      required
                  />
                </div>
                {error && (
                  <div className="alert alert-danger p-2 form-error-alert" role="alert">
                    <AlertCircle size={18} /> {error}
                  </div>
                )}
                {message && (
                  <div className="alert alert-success p-2 form-error-alert" role="alert">
                    <CheckCircle size={18} /> {message}
                  </div>
                )}
                <button
                  type="submit"
                  className="btn btn-primary btn-lg w-100 py-2 fw-bold rounded-pill"
                  disabled={loading || !!message}
                >
                  {loading ? "Sending..." : "Send Reset Link"}
                </button>
              </form>
              <p className="text-center mt-3">
                Remembered your password?{" "}
                <Link to="/login" className="link-primary">
                  Back to Login
                </Link>
              </p>
            </div>
          </div>
        </div>
        </div>
    </div>
  );
};

export default ForgotPassword;