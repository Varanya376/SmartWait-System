import { useState, useEffect } from "react";
import BackButton from "../components/BackButton";

function Profile({ profile, setProfile }) {

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const [preferences, setPreferences] = useState({
    italian: false,
    asian: false,
    american: false,
    mexican: false,
    thai: false
  });

  const [maxWait, setMaxWait] = useState(20);
  const [maxDistance, setMaxDistance] = useState(1);

  //LOAD EXISTING PROFILE
  useEffect(() => {
    if (profile) {
      setPreferences(profile.preferences || {});
      setMaxWait(profile.maxWait || 20);
      setMaxDistance(profile.maxDistance || 1);
    }
  }, [profile]);

  const handleCheckbox = (type) => {
    setPreferences({
      ...preferences,
      [type]: !preferences[type]
    });
  };

  return (
    <div className="app-container">

      <BackButton label="Back to Restaurants" />

      <div className="header">
        <h1 className="app-title">Synq</h1>
        <p className="tagline">YOUR PROFILE & PREFERENCES</p>
      </div>

      <div className="profile-container">
        <div className="profile-card">

          <h2>Your Details</h2>

          <div className="profile-input">
            👤
            <input
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="profile-input">
            📧
            <input
              placeholder="Your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <h2>Cuisine Preferences</h2>

          <div className="cuisine-list">
            {["italian","asian","american","mexican","thai"].map((c) => (
              <label key={c}>
                <input
                  type="checkbox"
                  checked={preferences[c]}
                  onChange={() => handleCheckbox(c)}
                />
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </label>
            ))}
          </div>

          <h2>Your Tolerance</h2>

          <div className="slider-row">
            <div className="slider-label">
              <span>⏱ Max Wait Time</span>
              <span>{maxWait} min</span>
            </div>
            <input
              type="range"
              min="5"
              max="60"
              value={maxWait}
              onChange={(e) => setMaxWait(Number(e.target.value))}
            />
          </div>

          <div className="slider-row">
            <div className="slider-label">
              <span>📍 Max Distance</span>
              <span>{maxDistance} miles</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="5"
              step="0.1"
              value={maxDistance}
              onChange={(e) => setMaxDistance(Number(e.target.value))}
            />
          </div>

          <button
            className="profile-save-btn"
            onClick={() => {
              const data = {
                preferences,
                maxWait,
                maxDistance
              };

              setProfile(data); //GLOBAL UPDATE
              alert("Preferences saved!");
            }}
          >
            Save Preferences
          </button>

        </div>
      </div>

    </div>
  );
}

export default Profile;