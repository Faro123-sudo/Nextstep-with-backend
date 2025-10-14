// src/context/ProfileContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { getProfile } from '../utils/core';

const ProfileContext = createContext();

export const useProfile = () => useContext(ProfileContext);

export const ProfileProvider = ({ children }) => {
    const [profile, setProfile] = useState(null); // Start with null
    const [loading, setLoading] = useState(true);

    const fetchProfile = async () => {
        try {
            const userProfile = await getProfile();
            // Store the entire profile object (or null if fetch fails)
            setProfile(userProfile);
        } catch (err) {
            console.error("Profile fetch failed:", err);
            setProfile(null);
        } finally {
            setLoading(false);
        }
    };

    // Run once on component mount
    useEffect(() => {
        // Only fetch profile if there isn't one already (e.g., from login)
        if (!profile) {
            fetchProfile();
        }
    }, []); // Dependency array is empty, so this runs only once on initial mount

    // Function to manually refresh profile after actions like username change
    const refreshProfile = () => {
        setLoading(true);
        fetchProfile();
    };

    return (
        <ProfileContext.Provider value={{ profile, loading, refreshProfile, setProfile, setLoading }}>
            {children}
        </ProfileContext.Provider>
    );
};