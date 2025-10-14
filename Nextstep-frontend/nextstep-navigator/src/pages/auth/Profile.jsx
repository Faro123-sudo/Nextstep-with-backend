import React, { useEffect, useState } from "react";
import "./Profile.css";
import defaultProfilePic from "../../assets/default-profile.webp"; // <-- Default profile picture
const Profile = ({ user }) => {
    const [tagsMap, setTagsMap] = useState({});

    // Fetch tags once so we can map interest IDs to names
    useEffect(() => {
        const fetchTags = async () => {
            try {
                const res = await fetch((import.meta.env.VITE_API_URL || "http://localhost:8000/api") + "/core/tags/");
                if (!res.ok) return;
                const data = await res.json();
                // data likely list of {id, name, slug}
                const map = {};
                data.forEach((t) => (map[t.id] = t.name));
                setTagsMap(map);
            } catch (err) {
                // ignore
            }
        };
        fetchTags();
    }, []);

    // ✅ Profile Display State ✅
    // The API may pass either:
    // 1) a `profile` object that contains `{ user: { ... }, profile_image, bio, ... }`
    // 2) or a plain `user` object (with fields pulled from profile via serializer but no profile_image)
    if (user) {
        // Normalize so we have a consistent `profileObj` (top-level profile) and `displayUser` (user fields)
        const profileObj = user.user ? user : { user };
        const displayUser = profileObj.user;

        // Derive unified values so JSX is simple and has no nested OR checks
        const profileImage = profileObj.profile_image
            ? String(profileObj.profile_image)
            : (displayUser.profile_image ? String(displayUser.profile_image) : defaultProfilePic);

        const bio = profileObj.bio || displayUser.bio || "";
        const education = profileObj.education_level || displayUser.education_level || "";
        const interests = (profileObj.interests && profileObj.interests.length) ? profileObj.interests : (displayUser.interests || []);

        return (
            // ... inside the return statement
<div className="profile-page-container d-flex flex-column align-items-center justify-content-center py-5">
    {/* Adjusted: Added 'py-5' for vertical padding on the page */}
    <div className="profile-card p-4 bg-white shadow-lg rounded-4 text-center">
        {/* Adjusted: 'p-5' reduced to 'p-4', 'rounded-3' increased to 'rounded-4', 'text-left' removed (made 'text-center' below) */}
        
        {/* Profile Icon/Avatar */}
        <div className="avatar-placeholder mb-4 mx-auto">
            {/* Added: shadow class for a subtle lift */}
            <img 
                src={profileImage} 
                alt="Profile" 
                className="img-fluid rounded-circle custom-avatar shadow-sm" // Added shadow-sm
            />
        </div>

        {/* Username */}
        <h4 className="display-6 fw-bold mb-1 text-center">
            {/* Changed to use one color for better focus, removing the span */}
            {displayUser.username} 
        </h4>
        {/* Adjusted: Added h6 for secondary text and made it text-muted */}
        <h6 className="text-muted mb-3">{displayUser.first_name} {displayUser.last_name}</h6> 

        {/* Bio */}
        {bio && (
            <p className="text-secondary text-center mt-2 mb-4 fst-italic">
                "{bio}"
            </p>
        )}

        {/* User Details */}
        <div className="details-section mt-4 pt-4 border-top">
            <div className="text-start"> {/* Added a wrapper to left-align the details */}
                
                {/* Email - Using a badge for better visual distinction */}
                <p className="mb-2">
                    <span className="fw-semibold text-dark me-2">Email:</span> 
                    <span className="badge text-bg-light border text-primary">{displayUser.email}</span>
                </p>

                {/* Role */}
                <p className="mb-2">
                    <span className="fw-semibold text-dark me-2">Role:</span>{" "}
                    <span className="badge bg-primary text-white text-capitalize">{displayUser.role}</span>
                </p>
                
                {/* Education */}
                {education && education !== 'other' && (
                    <p className="mb-2">
                        <span className="fw-semibold text-dark me-2">Education:</span>{""}
                        <span className="text-capitalize">{education}</span>
                    </p>
                )}

                {/* Interests (if available) - Using Pill Badges */}
                {interests && interests.length > 0 && (
                    <div className="mb-3">
                        <span className="fw-semibold text-dark d-block mb-1">Interests:</span>{" "}
                        <div className="d-flex flex-wrap gap-2">
                            {interests.map((i) => (
                                <span 
                                    key={i} 
                                    className="badge  text-bg-secondary" // Used text-bg-info for a nice light blue/cyan color
                                >
                                    {tagsMap[i] || i}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>

    </div>
    <div className="upload-section mt-4 text-center">
        <a href="/profileSetting" className="btn btn-primary btn-lg rounded-pill">
            Edit Profile ✏️
        </a>
    </div>
</div>
// ...
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