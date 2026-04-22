import { useNavigate } from "react-router-dom";
import { useState } from "react";

function Register() {
  const navigate = useNavigate();

const [name, setName] = useState("");
const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [confirmPassword, setConfirmPassword] = useState("");



const handleSubmit = async (e) => {
  e.preventDefault();

  if (password !== confirmPassword) {
    alert("Passwords do not match");
    return;
  }

  if (password.length < 6) {
    alert("Password must be at least 6 characters");
    return;
  }

  try {
    const res = await fetch("http://localhost:8000/api/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email,
        password,
        name
      })
    });

    let data;

    try {
      data = await res.json();
    } catch {
      throw new Error("Server error (not JSON)");
    }

    if (!res.ok) {
      throw new Error(data.error || "Registration failed");
    }

    console.log("✅ Registered:", data);

    //redirect to login after success
    navigate("/");

  } catch (err) {
    console.error("❌ Register error:", err);
    alert(err.message);
  }
};

  return (
    <div className="login-page">

      {/* BACK BUTTON */}
      <button
        className="back-btn"
        onClick={() => navigate("/")}
      >
        ← Back to Login
      </button>

      {/* HEADER */}
      <div className="login-header">
        <h1 className="app-title">Synq</h1>
        <p className="tagline">USER REGISTRATION</p>
      </div>

      {/* CARD */}
      <div className="login-card">

        <h2>Create Your Account</h2>
        <p className="login-subtext">
          Register to start using Sync
        </p>

        <div className="card-divider" />

        <form onSubmit={handleSubmit}>

          <div className="input-row">
            <span>👤</span>
            <input
              type="text"
              placeholder="Full Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="input-row">
            <span>📧</span>
            <input
              type="email"
              placeholder="Email Address"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="input-row">
            <span>🔒</span>
            <input
              type="password"
              placeholder="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="input-row">
            <span>🔒</span>
            <input
            type="password"
            placeholder="Confirm Password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          </div>

          <button type="submit" className="login-btn">
            Register
          </button>

        </form>

        {/* LINKS */}
        <div className="login-links">
          <span
            className="link"
            onClick={() => navigate("/")}
          >
            Already have an account? Login here
          </span>
        </div>

      </div>
    </div>
  );
}

export default Register;