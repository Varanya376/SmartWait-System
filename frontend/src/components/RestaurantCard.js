import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchWaitTime } from "../services/api";


// SCORE FUNCTION
function calculateScore(restaurant, wait, factors, mlUsed, distance) {
  const safeDistance = distance ?? 5;

  if (!mlUsed || !factors) {
    let score = 100;
    score -= (wait ?? 20) * 1.5;
    score -= safeDistance * 20;
    score += (restaurant.rating || 0) * 5;
    score -= (restaurant.crowd || 0) * 5;

    return Math.max(50, Math.min(100, Math.round(score)));
  }

  let score = 100;

  score -= wait * 2;

  const queuePressure = factors.queue_length / Math.max(1, factors.total_tables);
  score -= queuePressure * 40;

  const occupancy = factors.occupied_tables / Math.max(1, factors.total_tables);
  score -= occupancy * 30;

  if (safeDistance < 1) score -= safeDistance * 5;
  else if (safeDistance < 5) score -= safeDistance * 10;
  else score -= safeDistance * 20;

  score += (restaurant.rating || 0) * 6;

  return Math.max(0, Math.min(100, Math.round(score)));
}

function scoreClass(score) {
  if (score >= 85) return "high";
  if (score >= 70) return "medium";
  return "low";
}

function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;

  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI/180) *
    Math.cos(lat2 * Math.PI/180) *
    Math.sin(dLon/2) *
    Math.sin(dLon/2);

  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
}

function RestaurantCard({
  restaurant,
  userLocation,
  saved,
  toggleSave,
  tag,
  joinQueue,
  leaveQueue,
  isJoined,
  simulateRush
}) {
  const navigate = useNavigate();

  const [wait, setWait] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [explanation, setExplanation] = useState([]);

  const isSaved = saved?.includes(restaurant.id);

  const handleClick = () => {
    navigate(`/restaurant/${restaurant.id}`);
  };

  const [mlUsed, setMlUsed] = useState(false);
  const [factors, setFactors] = useState(null);

  const lat = parseFloat(restaurant.lat);
  const lng = parseFloat(restaurant.lng);

  const realDistance =
    userLocation && !isNaN(lat) && !isNaN(lng)
      ? getDistance(userLocation.lat, userLocation.lng, lat, lng)
      : null;

    const score = calculateScore(restaurant, wait, factors, mlUsed, realDistance);


  // OPTIMIZED WAIT FETCH (no API spam)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchWaitTime(restaurant.id);
        setWait(data.wait_time);
        setConfidence(data.confidence);
        setMlUsed(data.ml_used);
        setFactors(data.factors);
        setExplanation(data.explanation || []);
      } catch {
        setWait(20);
        setConfidence(70);
      }
    };

    fetchData(); // initial call

    const interval = setInterval(fetchData, 30000); // every 30 sec 

    return () => clearInterval(interval);
  }, [restaurant.id]);

  return (
    <div className="restaurant-card" onClick={handleClick}>

      {tag && <div className="tag-badge">{tag}</div>}

      {/* SAVE BUTTON */}
      <div
        className="heart-icon"
        onClick={(e) => {
          e.stopPropagation();
          toggleSave(Number(restaurant.id));
        }}
      >
        {isSaved ? "❤️" : "🤍"}
      </div>

      <div className="card-header">
        <h2>{restaurant.name}</h2>
        <p>{restaurant.category}</p>
      </div>

      {/* WAIT TIME */}
      <div className="wait-badge">
        ⏱ {wait !== null ? `${Math.max(1, wait)} MIN WAIT` : "Loading..."}
      </div>

      {/* CONFIDENCE */}
      <p className="confidence">
        🤖 {confidence !== null ? `${confidence}% confidence` : "Calculating..."}
      </p>

      {/* AI SECTION */}
      {mlUsed && (
        <div className="ml-section">

        <div className="ml-badge">
            🤖 AI Prediction
        </div>

      {factors && (
        <div className="ml-explanation">
          Queue: {factors.queue_length} • 
          Occupancy: {factors.occupied_tables}/{factors.total_tables}
        </div>
      )}

      {/* NEW EXPLANATION */}
        {explanation.length > 0 && (
          <p className="ml-explanation">
              🧠 {explanation.join(", ")}
          </p>
      )}

  </div>
)}

      <div className="card-details">
        <div>
        <p className="distance">
          📍 {realDistance
          ? `${realDistance.toFixed(1)} km away`
          : "Enable location"}
        </p>
        </div>
        <div>⭐ {restaurant.rating}</div>

        <div>
          🤖 Score:
          <span className={scoreClass(score)}> {score}%</span>
        </div>
      </div>

      {/* SIMULATE RUSH */}
      <button
        onClick={(e) => {
        e.stopPropagation();
        simulateRush(); 
      }}
>
        🚀 Simulate Rush
</button>

      {/* JOIN / LEAVE QUEUE */}
      <button
        className={`join-btn ${isJoined ? "leave" : ""}`}
        onClick={(e) => {
          e.stopPropagation();
          isJoined
            ? leaveQueue(restaurant.id)
            : joinQueue(restaurant.id, restaurant.name);
        }}
      >
        {isJoined ? "Leave Queue" : "Join Queue"}
      </button>

    </div>
    );
  }

export default RestaurantCard;