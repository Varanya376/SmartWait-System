import { useNavigate, useLocation } from "react-router-dom";

function BackButton({ fallback = "/home", label = "Back to Restaurants" }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleBack = () => {
    if (location.state?.from) {
      navigate(location.state.from);
    } else {
      navigate(fallback);
    }
  };

  return (
    <button className="back-btn floating" onClick={handleBack}>
      ← {label}
    </button>
  );
}

export default BackButton;