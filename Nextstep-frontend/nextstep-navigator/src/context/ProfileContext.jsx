// src/context/ProfileContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { getProfile, getAccessToken } from '../utils/auth'; // Import your auth functions

const ProfileContext = createContext();

export const useProfile = () => useContext(ProfileContext);

export const ProfileProvider = ({ children }) => {
    const [profile, setProfile] = useState({ username: null, role: 'guest' });
    const [loading, setLoading] = useState(true);

    const fetchProfile = async () => {
        if (!getAccessToken()) {
            setProfile({ username: null, role: 'guest' });
            setLoading(false);
            return;
        }
        try {
            const userProfile = await getProfile();
            if (userProfile) {
                setProfile({
                    firstName: userProfile.first_name || null,
                    lastName: userProfile.last_name || null,
                    username: userProfile.username || null,
                    role: userProfile.role || 'guest',
                    email: userProfile.email || null
                });
            } else {
                setProfile({ username: null, role: 'guest' });
            }
        } catch (err) {
            console.error("Profile fetch failed:", err);
            setProfile({ username: null, role: 'guest' });
        } finally {
            setLoading(false);
        }
    };

    // Run once on component mount
    useEffect(() => {
        fetchProfile();
    }, []);

    // Function to manually refresh profile after actions like username change
    const refreshProfile = () => {
        setLoading(true);
        fetchProfile();
    };

    return (
        <ProfileContext.Provider value={{ profile, loading, refreshProfile, setProfile }}>
            {children}
        </ProfileContext.Provider>
    );
};