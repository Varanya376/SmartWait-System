import { useParams } from "react-router-dom";
import QueueStatus from "../components/QueueStatus";
import JoinQueue from "../components/JoinQueueButton";
import BackButton from "../components/BackButton";
import { useEffect, useState } from "react";
import { fetchWaitTime, subscribeToAlert } from "../services/api";

// Smart score
function calculateScore(restaurant, wait) {
  let score = 100;

  score -= (restaurant.distance ?? 5) * 15;
  score += (restaurant.rating || 0) * 5;
  score -= (restaurant.crowd || 0) * 5;
  score -= (wait || 10);

  return Math.max(0, score);
}

// Distance function
function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;

  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

function Restaurant({ saved, toggleSave }) {
  const { id } = useParams();

  const [restaurant, setRestaurant] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [wait, setWait] = useState(0);
  const [userLocation, setUserLocation] = useState(null);
  const [confidence, setConfidence] = useState(null);

  const [isJoined, setIsJoined] = useState(false);
  const [currentUserName] = useState(() => {
    let username = localStorage.getItem("username");
    if (!username) {
      username = "User_" + Math.floor(Math.random() * 10000);
      localStorage.setItem("username", username);
    }
    return username;
  });

const [alertEnabled, setAlertEnabled] = useState(false);
const ALERT_THRESHOLD = 5;


useEffect(() => {
  const checkQueue = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/queue/", {
        credentials: "include"
      });
        
      const data = await res.json();

      const mine = data.find(
        q =>
          q.restaurant === Number(id) &&
          q.name === currentUserName &&
          (q.status === "waiting" || q.status === "seated")
      );

      setIsJoined(!!mine);

    } catch (err) {
      console.error("Queue check error:", err);
    }
  };

  checkQueue();
}, [id, currentUserName]);


  // GET USER LOCATION
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      (err) => {
        console.error("Location error:", err);

        // fallback (London)
        setUserLocation({
          lat: 51.5074,
          lng: -0.1278,
        });
      }
    );
  }, []);

  // FETCH RESTAURANT
  useEffect(() => {
    fetch(`http://localhost:8000/api/restaurants/${id}/`)
      .then(res => res.json())
      .then(data => {
        setRestaurant({
          ...data,
          rating: Number((Math.random() * 2 + 3).toFixed(1)),
          crowd: Math.floor(Math.random() * 5) + 1,
        });
      });
  }, [id]);


  // LIVE WAIT UPDATE
  useEffect(() => {
    const fetchWait = async () => {
      try {
        const data = await fetchWaitTime(id);
        setWait(data.wait_time);
        setConfidence(data.confidence);
      } catch (err) {
        console.error("Wait fetch error:", err);
      }
    };

    fetchWait();
    const interval = setInterval(fetchWait, 30000);

    return () => clearInterval(interval);
  }, [id]);


  // ALERT TRIGGER
  useEffect(() => {
    if (alertEnabled && wait <= ALERT_THRESHOLD) {
      setNotifications(prev => [
        ...prev,
        { id: Date.now(), message: "⏰ Wait time is now under 5 mins!" }
      ]);
      setAlertEnabled(false);
    }
  }, [wait, alertEnabled]);

  if (!restaurant) {
    return <div className="app-container">Loading...</div>;
}

  const lat = parseFloat(restaurant.lat);
  const lng = parseFloat(restaurant.lng);

  const realDistance =
    userLocation && !isNaN(lat) && !isNaN(lng)
      ? getDistance(userLocation.lat, userLocation.lng, lat, lng)
      : null;

  const score = calculateScore(
      { ...restaurant, distance: realDistance },
      wait
    );
  const isSaved = saved?.includes(restaurant.id);

    return (
      <div className="app-container">
    
        {/* TOASTS */}
        <div className="toast-container">
          {notifications.map(n => (
            <div key={n.id} className="toast">
              {n.message}
            </div>
          ))}
        </div>
    
        <BackButton />

      <div className="header">
        <h1 className="app-title">SmartWait</h1>
        <p className="tagline">RESTAURANT DETAILS</p>
      </div>

      <div className="restaurants-grid">
        <div className="restaurant-card">

          <div
            className="heart-icon"
            onClick={() => toggleSave(restaurant.id)}
          >
            {isSaved ? "❤️" : "🤍"}
          </div>

          <div className="card-header">
            <h2 className="restaurant-title">{restaurant.name}</h2>
            <p className="restaurant-sub">
              {restaurant.category?.charAt(0).toUpperCase() + restaurant.category?.slice(1)} •{" "}
              {realDistance !== null
                  ? `📍${realDistance.toFixed(1)} km away`
                  : "📍 Enable location"}
            </p>
          </div>

          <div className="detail-item">
            👥 Crowd: {restaurant.crowd}/5
          </div>

          <p className="card-description">
            A popular dining destination known for its authentic flavours and vibrant atmosphere.
          </p>

          <QueueStatus wait={wait} crowd={restaurant.crowd} />

          <div className="ai-box">
            🤖 <strong>Smart Insight:</strong> Your estimated wait is around{" "}
            <strong>{Math.max(1, wait)} mins</strong>
          </div>

          <p className="confidence">
            🤖 Prediction Confidence: {confidence ?? "..."}%
          </p>

          <div className="card-details">
            <div className="detail-item">
              📍 {
                  realDistance !== null
                    ? `${realDistance.toFixed(1)} km away`
                    : "Enable location"
              }
            </div>
            <div className="detail-item">
              ⭐ Rating: {restaurant.rating ?? "Calculating..."}
            </div>

            <div className="detail-item">
              🤖 Smart Score:
              <span
                className={`smart-score ${score >= 85 ? "high" : score >= 70 ? "medium" : "low"
                  }`}
              >
                {" "}{score}%
              </span>
            </div>
          </div>

          <div className="map-container">
            <iframe
              title="map"
              width="100%"
              height="200"
              style={{ border: 0 }}
              loading="lazy"
              allowFullScreen
              src={
                restaurant.lat && restaurant.lng
                  ? `https://www.google.com/maps?q=${restaurant.lat},${restaurant.lng}(${restaurant.name})&z=17&output=embed`
                  : `https://www.google.com/maps?q=London&output=embed`
              }

            />
          </div>

          <div className="button-row">
          <button
              className="menu-btn"
              onClick={() => {
                  if (restaurant.menu_url) {
                    window.open(restaurant.menu_url, "_blank");
                  } else {
                    alert("Menu not available");
            }
          }}
  >
     View Menu
</button>

            <button
              className="menu-btn"
              onClick={() => {
                if (!alertEnabled) {
                  setAlertEnabled(true);
              
                  subscribeToAlert(restaurant.id); // 🔥 NEW
              
                  alert("🔔 Alert enabled! We’ll notify you when wait drops.");
                }
              }}
            >
              Enable Alert
            </button>
          </div>

          <JoinQueue
              restaurant={restaurant}
              isJoined={isJoined}
              setIsJoined={setIsJoined}
          />

        </div>
      </div>
    </div>
  );
}
export default Restaurant;