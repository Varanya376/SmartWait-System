import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { loginUser } from "../services/api";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ---------------- LOGIN ----------------
  const handleLogin = async () => {
    try {
      const data = await loginUser(email, password);
  
      console.log("✅ Logged in:", data);
  
      // ROLE-BASED REDIRECT
      if (data.role === "staff") {
        navigate(`/staff/${data.restaurant_id}`);
      } else {
        navigate("/home");
      }
  
    } catch (err) {
      console.error("❌ Login error:", err);
      alert(err.message);
    }
  };

  return (
    <div className="login-page">

      {/* HEADER */}
      <div className="login-header">
        <h1 className="app-title">SmartWait</h1>
        <p className="tagline">USER LOGIN</p>
      </div>

      {/* CARD */}
      <div className="login-card">

        <h2>Welcome Back</h2>
        <p className="login-subtext">
          Login to continue to SmartWait
        </p>

        <div className="card-divider" />

        {/* EMAIL */}
        <div className="input-row">
          <span className="input-icon">📧</span>
          <input
            type="text"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        {/* PASSWORD */}
        <div className="input-row">
          <span className="input-icon">🔒</span>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {/* BUTTON */}
        <button className="login-btn" onClick={handleLogin}>
          Login
        </button>

        {/* LINKS */}
        <div className="login-links">
          <span className="link" onClick={() => navigate("/register")}>
            Register
          </span>

          <span
            className="link"
            onClick={() => navigate("/forgot")}
          >
            Forgot Password?
          </span>

          <span
            className="staff-link"
            onClick={() => navigate("/staff-login")}
          >
            Restaurant staff? <b>Login here</b>
          </span>
        </div>

      </div>
    </div>
  );
}
export default Login;