import React from "react";
import "./Profile.css";
import defaultProfilePic from "../assets/default-profile.webp"; // <-- Default profile picture
const Profile = ({ user }) => {

    // Determine what to display in the avatar
    const avatarContent = defaultProfilePic ? (
        <img src={defaultProfilePic} alt="Profile" className="img-fluid rounded-circle" />
    ) : (
        user.username.charAt(0).toUpperCase()
    );

    // ✅ Profile Display State ✅
    if (user) {return (
        <div className="profile-page-container d-flex align-items-center justify-content-center">
            <div className="profile-card p-5 bg-white shadow-lg rounded-3 text-center">
                {/* Profile Icon/Avatar */}
                <div className="avatar-placeholder mb-4 mx-auto">
                    {avatarContent} {/* <-- Conditional content here */}
                </div>

                {/* Username */}
                <h1 className="display-6 fw-bold mb-1">
                    <span className="text-primary">{user.username}</span>
                </h1>

                {/* User Details */}
                <div className="details-section mt-4 pt-3 border-top">
                    <p className="text-muted mb-1 small">
                        <span className="fw-semibold">Email:</span> {user.email}
                    </p>
                    <p className="text-muted mb-0 small">
                        <span className="fw-semibold">Role:</span>{" "}
                        <span className="badge bg-info text-dark">{user.role}</span>
                    </p>
                </div>
            </div>
        </div>
    );
    }
    // 🚫 Error State 🚫
    else {
        return (
            <div className="d-flex align-items-center justify-content-center">
                <div className="alert alert-danger shadow-sm" role="alert">
                    <h4 className="alert-heading">Profile Load Error!</h4>
                    <p className="fw-semibold mb-0">
                        Could not load profile. Please log in again.
                    </p>
                </div>
            </div>
        );
    }

};

export default Profile;