import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useProfile } from "../../context/ProfileContext";
import { updateProfile } from "../../utils/core";

export default function ProfileSetting({ user }) {
    const navigate = useNavigate();
    const { refreshProfile } = useProfile(); // Get the refresh function from context

    // Form state, initialized with user data
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        email: "",
        bio: "",
        education_level: "other",
        profile_image: null,
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [previewImage, setPreviewImage] = useState(null);
    const [availableTags, setAvailableTags] = useState([]);
    const [selectedInterests, setSelectedInterests] = useState([]);

    // Pre-fill form with existing user data
    useEffect(() => {
        if (user) {
            setFormData({
                first_name: user.first_name || "",
                last_name: user.last_name || "",
                email: user.email || "",
                bio: user.bio || "",
                education_level: user.education_level || "other",
                profile_image: null, // Don't pre-fill file input
            });
            // Pre-select interests if provided on user
            if (user.interests && Array.isArray(user.interests)) {
                setSelectedInterests(user.interests);
            }
        }
    }, [user]);

    // Load available tags for interests
    useEffect(() => {
        const fetchTags = async () => {
            try {
                const res = await fetch((import.meta.env.VITE_API_URL || "http://localhost:8000/api") + "/core/tags/");
                if (!res.ok) return;
                const data = await res.json();
                setAvailableTags(data);
            } catch (err) {
                console.error("Failed to load tags:", err);
            }
        };
        fetchTags();
    }, []);

    const handleChange = (e) => {
        const { name, value, files } = e.target;
        if (name === "profile_image" && files && files[0]) {
            const file = files[0];
            setFormData((prev) => ({ ...prev, profile_image: file }));
            setPreviewImage(URL.createObjectURL(file));
        } else {
            setFormData((prev) => ({ ...prev, [name]: value }));
        }
    };

    const handleInterestToggle = (tagId) => {
        setSelectedInterests((prev) => {
            if (prev.includes(tagId)) return prev.filter((id) => id !== tagId);
            return [...prev, tagId];
        });
    };

    // Cleanup the object URL on component unmount
    useEffect(() => {
        return () => {
            if (previewImage) {
                URL.revokeObjectURL(previewImage);
            }
        };
    }, [previewImage]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setSuccess("");

        try {
            // Construct FormData to support files and multiple interests
            const payload = new FormData();
            for (const key in formData) {
                if (formData[key] !== null && formData[key] !== undefined) {
                    payload.append(key, formData[key]);
                }
            }
            // Append interests as repeated field entries (Django will accept list of ids)
            selectedInterests.forEach((id) => payload.append("interests", id));

            await updateProfile(payload);
            setSuccess("Profile updated successfully!");
            await refreshProfile(); // Refresh the profile data globally
            setTimeout(() => navigate("/profile"), 1500); // Redirect after a short delay
        } catch (err) {
            setError("Failed to update profile. Please try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div className="profile-setting-page-container d-flex flex-column align-items-center justify-content-center">
                <div className="profile-card p-5 bg-white shadow-lg rounded-3 text-center">
                    <h2 className="mb-4 fw-bold text-primary">Profile Settings</h2>

                    {error && <div className="alert alert-danger">{error}</div>}
                    {success && <div className="alert alert-success">{success}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="mb-3 text-start">
                            <label htmlFor="first_name" className="form-label">First Name</label>
                            <input type="text" className="form-control" id="first_name" name="first_name" value={formData.first_name} onChange={handleChange} placeholder="Enter your first name" />
                        </div>
                        <div className="mb-3 text-start">
                            <label htmlFor="last_name" className="form-label">Last Name</label>
                            <input type="text" className="form-control" id="last_name" name="last_name" value={formData.last_name} onChange={handleChange} placeholder="Enter your last name" />
                        </div>
                        <div className="mb-3 text-start">
                            <label htmlFor="email" className="form-label">Email</label>
                            <input type="email" className="form-control" id="email" name="email" value={formData.email} onChange={handleChange} placeholder="Enter your email" />
                        </div>
                        <div className="mb-3 text-start">
                            <label htmlFor="bio" className="form-label">Bio</label>
                            <textarea className="form-control" id="bio" name="bio" value={formData.bio} onChange={handleChange} rows="3" placeholder="Tell us about yourself..."></textarea>
                        </div>
                        <div className="mb-3 text-start">
                            <label htmlFor="education_level" className="form-label">Education Level</label>
                            <select className="form-select" id="education_level" name="education_level" value={formData.education_level} onChange={handleChange}>
                                <option value="none">None</option>
                                <option value="primary">Primary</option>
                                <option value="secondary">Secondary</option>
                                <option value="diploma">Diploma</option>
                                <option value="bachelors">Bachelors</option>
                                <option value="masters">Masters</option>
                                <option value="phd">PhD</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div className="mb-3 text-start">
                            <label htmlFor="profile_image" className="form-label">Profile Image</label>
                            <input type="file" className="form-control" id="profile_image" name="profile_image" onChange={handleChange} accept="image/*" />
                        </div>

                        {/* Interests selection */}
                        <div className="mb-3 text-start">
                            <label className="form-label">Interests</label>
                            <div className="d-flex flex-wrap">
                                {availableTags.map((tag) => (
                                    <div key={tag.id} className="form-check me-2">
                                        <input
                                            className="form-check-input"
                                            type="checkbox"
                                            id={`tag-${tag.id}`}
                                            checked={selectedInterests.includes(tag.id)}
                                            onChange={() => handleInterestToggle(tag.id)}
                                        />
                                        <label className="form-check-label ms-1" htmlFor={`tag-${tag.id}`}>
                                            {tag.name}
                                        </label>
                                    </div>
                                ))}
                            </div>
                        </div>
                        {previewImage && (
                            <div className="mb-3 text-center">
                                <img src={previewImage} alt="Profile Preview" className="img-fluid rounded-circle" style={{ width: "150px", height: "150px", objectFit: "cover" }} />
                            </div>
                        )}
                        <button type="submit" className="btn btn-primary mt-3" disabled={loading}>
                            {loading ? "Saving..." : "Save Changes"}
                        </button>
                    </form>
                </div>
            </div>
        </>
    );
}