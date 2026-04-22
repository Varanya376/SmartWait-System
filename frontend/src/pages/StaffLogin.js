import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/api";

function StaffLogin() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          password
        })
      });
  
      const data = await res.json();
  
      if (!res.ok) throw new Error(data.error || "Login failed");
  
      // CHECK ROLE
      if (data.role !== "staff") {
        alert("❌ Not a staff account");
        return;
      }
  
      // CHECK RESTAURANT
      if (!data.restaurant_id) {
        alert("❌ No restaurant assigned to staff");
        return;
      }
  
      console.log("✅ Staff login success:", data);
  
      navigate(`/staff/${data.restaurant_id}`);
  
    } catch (err) {
      console.error("❌ Staff login error:", err);
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
        ← Back
      </button>
  
      {/* HEADER */}
      <div className="login-header">
        <h1 className="app-title">Synq</h1>
        <p className="tagline">STAFF LOGIN</p>
      </div>
  
      {/* CARD */}
      <div className="login-card">
  
        <h2>Staff Access</h2>
        <p className="login-subtext">
          Login to manage your restaurant
        </p>
  
        <div className="card-divider" />
  
        {/* EMAIL */}
        <div className="input-row">
          <span>📧</span>
          <input
            type="text"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
  
        {/* PASSWORD */}
        <div className="input-row">
          <span>🔒</span>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
  
        <button className="login-btn" onClick={handleLogin}>
          Login
        </button>
  
      </div>
    </div>
  );
}

export default StaffLogin;