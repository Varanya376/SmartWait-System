import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { sendOTP, verifyOTP } from "../services/api";

function ForgotPassword() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (step === 1) {
        const res = await sendOTP(email);
        alert(res.message || "OTP sent!");
        setStep(2);
      } else {
        const res = await verifyOTP(email, otp, password);
        alert(res.message || "Password reset successful!");
        navigate("/");
      }
    } catch (err) {
      alert("Something went wrong");
      console.error(err);
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
        <p className="tagline">RESET PASSWORD</p>
      </div>

      {/* CARD */}
      <div className="login-card">

        <h2>Forgot Your Password?</h2>

        <p className="login-subtext">
          {step === 1
            ? "Enter your registered email to receive an OTP."
            : "Enter the OTP sent to your email and set a new password."}
        </p>

        <div className="card-divider" />

        <form onSubmit={handleSubmit}>

          {/* STEP 1 */}
          {step === 1 && (
            <div className="input-row">
              <span>📧</span>
              <input
                type="email"
                placeholder="Registered Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}

          {/* STEP 2 */}
          {step === 2 && (
            <>
              <div className="input-row">
                <span>🔢</span>
                <input
                  type="text"
                  placeholder="Enter OTP"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  required
                />
              </div>

              <div className="input-row">
                <span>🔒</span>
                <input
                  type="password"
                  placeholder="New Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </>
          )}

          <button type="submit" className="login-btn">
            {step === 1 ? "Send OTP" : "Reset Password"}
          </button>

        </form>

        <div className="login-links">
          <span
            className="link"
            onClick={() => navigate("/")}
          >
            Back to Login
          </span>
        </div>

      </div>
    </div>
  );
}

export default ForgotPassword;