import React from "react";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { sendPasswordResetEmail } from "../utils/auth";
import Lottie from "lottie-react";
import Logo from "../assets/logo.webp";
import animationData from "../assets/animation/forgot-password.json";
import "bootstrap/dist/css/bootstrap.min.css";
import "../components/staticFiles/LandingPage.css";

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
        <h2 className="mb-4 text-center">Forgot Password</h2>
        <div className="container">
          <div className="row align-items-center">
            <div className="col-md-6 col-lg-5 text-center mb-5 mb-md-0" data-aos="fade-right" data-aos-delay="500">
              <Lottie animationData={animationData} loop style={{ width: "100%", maxWidth: "400px", margin: "auto" }} />
              <p className="lead mt-4 text-muted px-3">
                Enter your email address and we'll send you a link to reset your password.
              </p>
            </div>
            <div className="col-md-6 col-lg-5 offset-lg-1" data-aos="fade-left" data-aos-delay="700">
              <form onSubmit={handleSubmit} className="p-4 p-md-5 bg-white rounded shadow-sm">
                <div className="text-center mb-4">
                  < img src={Logo} alt="NextStep Navigator Logo" className="mb-3" style={{ height: "60px" }} />
                  <h3 className="fw-bold">NextStep Navigator</h3>
                </div> 
                <input
                    type="email"
                    className="form-control mb-3"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={!!message} // Disable input after success
                    required
                />
                {error && <p className="text-danger text-sm">{error}</p>}
                {message && <p className="text-success text-sm">{message}</p>}
                <button
                    type="submit"
                    className="btn btn-primary btn-lg w-100 py-2 fw-bold rounded-pill"
                    disabled={loading || !!message} // Disable button during/after request
                >
                    {loading ? "Sending..." : "Send Reset Link"}
                </button>
                <div className="mt-3 text-center">
                  <Link to="/login" className="text-decoration-none">
                    Back to Login
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
        </div>
        );
    };
    
    export default ForgotPassword;