import api from "./axiosClient";

/**
 * Fetches the profile for the currently authenticated user.
 * @returns {Promise<Object|null>} The user profile data or null on error.
 */
export const getProfile = async () => {
  try {
    const response = await api.get("/core/profile/");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch profile:", error);
    return null;
  }
};

/**
 * Updates the profile for the currently authenticated user.
 * Can handle file uploads.
 * @param {Object} profileData - The data to update.
 * @returns {Promise<Object>} The updated profile data.
 */
export const updateProfile = async (profileData) => {
  // Accept either a plain object or a FormData instance.
  let formData;
  if (profileData instanceof FormData) {
    formData = profileData;
  } else {
    // Build FormData to support file uploads (e.g., profile_image)
    formData = new FormData();
    // Append all key-value pairs from profileData to formData
    for (const key in profileData) {
      // Only append if the value is not null or undefined to avoid issues
      if (profileData[key] !== null && profileData[key] !== undefined) {
        formData.append(key, profileData[key]);
      }
    }
  }

  const response = await api.patch("/core/profile/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};
