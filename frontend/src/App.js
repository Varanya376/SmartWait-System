import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Restaurant from "./pages/Restaurant";
import Profile from "./pages/Profile";
import StaffDashboard from "./pages/StaffDashboard";
import Saved from "./pages/Saved";
import StaffLogin from "./pages/StaffLogin";
import ForgotPassword from "./pages/ForgotPassword";

function App() {

  // SAVED
  const [saved, setSaved] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("saved")) || [];
    } catch {
      return [];
    }
  });

  // PROFILE
  const [profile, setProfile] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("profile")) || {
        preferences: {},
        maxWait: 20,
        maxDistance: 1
      };
    } catch {
      return {
        preferences: {},
        maxWait: 20,
        maxDistance: 1
      };
    }
  });

  // sync localStorage
  useEffect(() => {
    localStorage.setItem("saved", JSON.stringify(saved));
  }, [saved]);

  useEffect(() => {
    localStorage.setItem("profile", JSON.stringify(profile));
  }, [profile]);

  // toggle save
  const toggleSave = (id) => {
    setSaved((prev) =>
      prev.includes(id)
        ? prev.filter((rid) => rid !== id)
        : [...prev, id]
    );
  };

  return (
    <Router>
      <Routes>

        <Route path="/" element={<Login />} />

        {/* HOME */}
        <Route
          path="/home"
          element={
            <Home
              saved={saved}
              toggleSave={toggleSave}
              profile={profile}
            />
          }
        />

        <Route path="/register" element={<Register />} />
        <Route path="/staff-login" element={<StaffLogin />} />
        <Route path="/forgot" element={<ForgotPassword />} />

        {/* RESTAURANT PAGE */}
        <Route
          path="/restaurant/:id"
          element={
            <Restaurant
              saved={saved}
              toggleSave={toggleSave}
            />
          }
        />

        {/* SAVED */}
        <Route
          path="/saved"
          element={
            <Saved
              saved={saved}
              toggleSave={toggleSave}
            />
          }
        />

        {/* PROFILE */}
        <Route
          path="/profile"
          element={
            <Profile
              profile={profile}
              setProfile={setProfile}
            />
          }
        />

        {/* STAFF ROUTES (FIXED) */}
        <Route path="/staff" element={<Navigate to="/staff/1" />} />
        <Route path="/staff/:id" element={<StaffDashboard />} />

        {/* FALLBACK */}
        <Route path="*" element={<Navigate to="/" />} />

      </Routes>
    </Router>
  );
}

export default App;