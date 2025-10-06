import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { resetPasswordConfirm } from "../utils/auth"; // We will create this function
import Lottie from "lottie-react";
import Logo from "../assets/logo.webp";
import animationData from "../assets/animation/forgot-password.json"; // Reusing the animation
import "bootstrap/dist/css/bootstrap.min.css";
import "../components/staticFiles/LandingPage.css";

const ResetPasswordConfirm = () => {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    // New state for show password checkbox
    const [showPassword, setShowPassword] = useState(false); 
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const uid = searchParams.get("uid");
    const token = searchParams.get("token");

    useEffect(() => {
        if (!uid || !token) {
            setError("Invalid password reset link. Please try again.");
        }
    }, [uid, token]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }
        if (!uid || !token) {
            setError("Missing required information from reset link.");
            return;
        }

        try {
            setLoading(true);
            setError("");
            setMessage("");
            // Assuming resetPasswordConfirm only needs the new password once if it's confirmed
            // Based on your original code, it takes both, so I'll keep it.
            await resetPasswordConfirm(uid, token, password, confirmPassword); 
            setMessage("Your password has been reset successfully! You can now log in.");
            setTimeout(() => navigate("/login"), 3000); // Redirect to login after 3 seconds
        } catch (err) {
            const errorMessage = err.response?.data?.detail || err.response?.data?.new_password || "Failed to reset password. The link may be invalid or expired.";
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };
    
    // Determine the input type based on the state
    const passwordInputType = showPassword ? "text" : "password";

    return (
        <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center landing-bg">
            <h1 className="mb-4 fw-bold text-primary text-center">Reset Your Password</h1>
            <div className="container">
                <div className="row align-items-center">
                    <div className="col-md-6 col-lg-5 text-center mb-5 mb-md-0">
                        <Lottie animationData={animationData} loop style={{ width: "100%", maxWidth: "400px", margin: "auto" }} />
                    </div>
                    <div className="col-md-6 col-lg-5 offset-lg-1">
                        <form onSubmit={handleSubmit} className="p-4 p-md-5 bg-white rounded shadow-sm">
                            <div className="text-center mb-4">
                                <img src={Logo} alt="NextStep Navigator Logo" className="mb-3" style={{ height: "60px" }} />
                                <h3 className="fw-bold">NextStep Navigator</h3>
                            </div>
                            <p className="text-muted text-center mb-3">Enter your new password below.</p>
                            <input
                                type={passwordInputType}
                                className="form-control mb-3"
                                placeholder="New Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={!!message}
                                required
                            />
                            <input
                                type={passwordInputType}
                                className="form-control mb-3"
                                placeholder="Confirm New Password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                disabled={!!message}
                                required
                            />
                            
                            {/* NEW CHECKBOX */}
                            <div className="form-check mb-3">
                                <input
                                    className="form-check-input"
                                    type="checkbox"
                                    id="showPasswordCheck"
                                    checked={showPassword}
                                    onChange={() => setShowPassword(!showPassword)}
                                />
                                <label className="form-check-label" htmlFor="showPasswordCheck">
                                    Show Password
                                </label>
                            </div>
                            {/* END NEW CHECKBOX */}

                            {error && <p className="text-danger text-sm">{error}</p>}
                            {message && <p className="text-success text-sm">{message}</p>}
                            <button type="submit" className="btn btn-primary btn-lg w-100 py-2 fw-bold rounded-pill" disabled={loading || !!message}>
                                {loading ? "Resetting..." : "Reset Password"}
                            </button>
                            {message && <div className="mt-3 text-center"><Link to="/login" className="text-decoration-none">Go to Login</Link></div>}
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResetPasswordConfirm;