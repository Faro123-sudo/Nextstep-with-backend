// src/components/DisplayPages.jsx

import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import Breadcrumbs from "./Breadcrumbs";
import HomePage from "./HomePage";
import CareerBank from "./CareerBank";
// import Quiz from "./Quiz";
import Multimedia from "./MultimediaGuidance";
import Resources from "./ResourceLibrary";
import SuccessStories from "./SuccessStories";
import AdmissionCoaching from "./AdmissionAndCoaching";
import AboutUs from "./Aboutus";
import ContactUs from "./Contact";
import Footer from "./Footer";
import Feedback from "./Feedback";
import Profile from "../pages/auth/Profile";
import UploadStory from "./SuccessStory/UploadStory.jsx";
import ProfileSetting from "../pages/auth/ProfileSetting.jsx";
import Quiz from "../pages/auth/Quiz.jsx"; // Updated import path for Quiz

// Import the custom profile hook
import { useProfile } from "../context/ProfileContext";

// DisplayPages now receives the global onLogout handler from App.jsx as a prop
function DisplayPages({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  // Get user profile from the centralized context
  const { profile, loading } = useProfile();
  const user = profile?.user; // The profile from context is the user object.

  // This handleLogout calls the prop function passed from App.jsx.
  // That prop function handles: 1. API logout, 2. Local token clear, 3. Updating isAuthenticated state.
  const handleGlobalLogout = async () => {
    await onLogout(); // This runs the logout logic defined in App.jsx
    navigate("/login"); // Redirect after the global state is updated
  };

  const handleNavigate = (page) => {
    navigate(page === "home" ? "/" : `/${page}`);
  };

  const activeSection = location.pathname === "/" ? "home" : location.pathname.replace("/", "");
  const userType = user ? user.role : "guest";

  // Optional: Show loading state while profile is fetched on initial mount
  if (loading) {
    return <div>Loading user data...</div>;
  }

  return (
    <>
      <Header
        onNavigate={handleNavigate}
        activePage={activeSection}
        // Header now uses the profile from context (if you apply the Header fix)
        onLogout={handleGlobalLogout}
      />
      <main className="container">
        <Breadcrumbs activeSection={activeSection} userType={userType} onNavigate={handleNavigate} />

        <div className="max-w-4xl mx-auto p-4">
          <Routes>
            {/* Pass the user object derived from the context */}
            <Route path="*" element={<HomePage onNavigate={handleNavigate} user={user} />} />
            <Route path="/careerBank" element={<CareerBank userType={userType} />} />
            <Route path="/quiz" element={<Quiz userType={userType} />} />
            <Route path="/multimedia" element={<Multimedia userType={userType} />} />
            <Route path="/resources" element={<Resources userType={userType} />} />
            <Route path="/successStories" element={<SuccessStories userType={userType} />} />
            <Route path="/admissionCoaching" element={<AdmissionCoaching userType={userType} />} />
            <Route path="/aboutUs" element={<AboutUs />} />
            <Route path="/contact" element={<ContactUs />} />
            {/* Pass the full profile object to Profile so it can access top-level fields like profile_image */}
            <Route path="/profile" element={<Profile user={profile} />} />
            <Route path="/uploadStory" element={<UploadStory userType={userType} />} />
            <Route path="/profileSetting" element={<ProfileSetting user={user} />} />            
          </Routes>
        </div>
      </main>
      <Footer onNavigate={handleNavigate} />
      <Feedback />
    </>
  );
}

export default DisplayPages;