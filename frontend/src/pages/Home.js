import { useState, useEffect, useRef } from "react";
import logo from "../assets/synq-logo.png";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import RestaurantCard from "../components/RestaurantCard";
import MapView from "../components/MapView";
import { fetchWaitTime, fetchRestaurants, fetchQueue } from "../services/api";

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

function Home({ saved = [], toggleSave = () => {}, profile = {} }) {

  const [restaurants, setRestaurants] = useState([]);
  const lastNotificationRef = useRef(0);
  const [userLocation, setUserLocation] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [queueInfo, setQueueInfo] = useState({});
  const [showMap, setShowMap] = useState(false);
  const [notified, setNotified] = useState(false);
  const restaurantsRef = useRef([]);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    restaurantsRef.current = restaurants;
  }, [restaurants]);

  const notifiedRef = useRef(false);
  useEffect(() => {
    notifiedRef.current = notified;
  }, [notified]);

  const [currentUserName] = useState(() => {
    let saved = localStorage.getItem("username");
    if (!saved) {
      saved = "User_" + Math.floor(Math.random() * 10000);
      localStorage.setItem("username", saved);
    }
    return saved;
  });

  // GET USER LOCATION
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
      },
      () => {
        setUserLocation(null)
      }
    );
  }, []);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/queue/");
  
    socket.onopen = () => {
      console.log("✅ WebSocket connected");
    };
  
    socket.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("📡 WS data:", data);
    
        // Update queue directly from WS message 
        const queueData = data.queue || [];
    
        const formatted = queueData.map((q) => {
          const restaurantData = restaurantsRef.current.find(
            r => r.id === q.restaurant
          );
    
          return {
            restaurantId: q.restaurant,
            restaurant: restaurantData?.name || `Restaurant ${q.restaurant}`,
            position: q.position,
            wait: restaurantData?.wait_time ?? "Calculating...",
            status: q.status,
            name: q.name,
          };
        });
    
      
        const grouped = {};
        formatted.forEach(q => {
          if (!grouped[q.restaurantId]) grouped[q.restaurantId] = [];
          grouped[q.restaurantId].push(q);
        });
    
        let foundUser = false;
        const userQueues = {};
    
        Object.keys(grouped).forEach(rid => {
          const mine = grouped[rid].find(q => q.name === currentUserName);
          if (mine) {
            userQueues[rid] = [mine];
            foundUser = true;
          }
        });

        let someoneAtFront = false;

        for (let q of formatted) {

          // ONLY track YOUR user
          if (q.name !== currentUserName) continue;
        
          // TABLE READY
          if (q.status === "seated") {
            someoneAtFront = true;
        
            if (!notifiedRef.current) {
              setNotified(true);
        
              setNotifications(prev => {
                const updated = [
                  ...prev,
                  {
                    id: Date.now(),
                    message: "🎉 Your table is ready!",
                  },
                ];
                return updated.slice(-10);
              });
            }
            break;
          }
        
          // POSITION UPDATE
          if (q.status === "waiting") {
            const now = Date.now();
        
            console.log("MATCHED USER:", q.name, currentUserName);
        
            if (now - lastNotificationRef.current > 5000) {
              lastNotificationRef.current = now;
        
              setNotifications(prev => {
                const updated = [
                  ...prev,
                  {
                    id: Date.now(),
                    message: `📍 You're now #${q.position} in queue`,
                  },
                ];
                return updated.slice(-10);
              });
            }
          }
        }
        
        // reset notification state
        if (!someoneAtFront && notifiedRef.current) {
          setNotified(false);
          notifiedRef.current = false;
        }
        
        setQueueInfo(foundUser ? userQueues : {});
    
      } catch (err) {
        console.error("WS error:", err);
      }
    };
  
    socket.onclose = () => {
      console.log("❌ WebSocket disconnected");
    };
  
    return () => socket.close();
  }, [currentUserName]);

  // FETCH DATA FROM BACKEND
  useEffect(() => {
    if (!userLocation) return;
  
    fetchRestaurants()
      .then(async (data) => {
  
        const enriched = await Promise.all(
          data.map(async (r) => {
            try {
              const waitData = await fetchWaitTime(r.id);
        
              return {
                ...r,
                wait_time: waitData.wait_time,
                confidence: waitData.confidence,
        
                // ✅ ADD THESE
                factors: waitData.factors,
                mlUsed: waitData.ml_used,
        
                distance: getDistance(
                  userLocation.lat,
                  userLocation.lng,
                  r.lat,
                  r.lng
                ),
        
                rating: Number((Math.random() * 2 + 3).toFixed(1)),
                crowd: Math.floor(Math.random() * 5) + 1,
              };
            } catch {
              return {
                ...r,
                wait_time: 20,
              };
            }
          })
        );
  
        setRestaurants(
          enriched.sort((a, b) => (a.distance ?? 999) - (b.distance ?? 999))
        );
  
        //also refresh queue after load
        refreshQueue(enriched);
  
      })
      .catch((err) => console.error(err));
  
  }, [userLocation]);

  //SMART SCORE
  const calculateScore = (r) => {
    let score = 100;
  
    // Wait time (important)
    score -= (r.wait_time ?? 20) * 1.5;
  
    // Distance (reduced impact)
    score -= (r.distance ?? 5) * 4;
  
    // Rating boost
    score += (r.rating ?? 3) * 10;
  
    // Crowd penalty
    score -= (r.crowd ?? 3) * 4;
  
    // Bonus for low wait
    if ((r.wait_time ?? 20) <= 5) score += 10;
  
    return Math.max(0, Math.min(100, Math.round(score)));
  };

  //SORTING
  const sortRestaurants = (type) => {
    let sorted = [...restaurants];

    if (type === "rating") sorted.sort((a, b) => b.rating - a.rating);
    if (type === "distance") sorted.sort((a, b) => (a.distance ?? 999) - (b.distance ?? 999));

    if (type === "smart") {
      sorted.sort((a, b) => calculateScore(b) - calculateScore(a));
    }

    setRestaurants(sorted);
  };

// refresh queue info (positions + wait times)
const refreshQueue = async (restaurantListParam) => {
  const restaurantList = restaurantListParam || restaurants;

  try {
    const data = await fetchQueue();

    const queueFiltered = data.filter(
      q =>
        (q.status === "waiting" || q.status === "seated") &&
        q.name === currentUserName
    );

    const formatted = queueFiltered.map((q) => {
      const restaurantData = restaurantList.find(
        r => r.id === q.restaurant
      );

      return {
        restaurantId: q.restaurant,
        restaurant:
          restaurantData?.name || `Restaurant ${q.restaurant}`,
        position: q.position,
        wait:
          restaurantData?.wait_time !== undefined
            ? restaurantData.wait_time
            : "Calculating...",
        status: q.status,
        name: q.name,
      };
    });

    const grouped = {};
    formatted.forEach(q => {
      if (!grouped[q.restaurantId]) {
        grouped[q.restaurantId] = [];
      }
      grouped[q.restaurantId].push(q);
    });

    let foundUser = false;
    const userQueues = {};

    Object.keys(grouped).forEach(rid => {
      const mine = grouped[rid].find(
        q => q.name === currentUserName
      );

      if (mine) {
        userQueues[rid] = [mine];
        foundUser = true;
      }
    });

    if (foundUser) {
      setQueueInfo(userQueues);
    } else {
      setQueueInfo({});   
      setNotified(false); 
    }

  } catch (err) {
    console.error("❌ Queue refresh error:", err);
  }
};

  const joinQueue = async (restaurantId, restaurantName) => {
    try {
      const res = await fetch("http://localhost:8000/api/join_queue/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          restaurant: restaurantId,
          name: currentUserName,
          party_size: Math.floor(Math.random() * 4) + 1,
        }),
      });
  
      if (!res.ok) {
        throw new Error("Join queue failed");
      }
  
      const data = await res.json();
  
      if (data.status === "seated") {
        alert(`🎉 You're seated at ${restaurantName}!`);
        return;
      }
  
      const newEntry = {
        restaurantId,
        restaurant: restaurantName,
        position: data.position,
        wait: data.estimated_wait || 0,
        status: "waiting",
      };
  
      setQueueInfo((prev) => ({
        ...prev,
        [restaurantId]: [newEntry],
      }));
  
    } catch (err) {
      console.error("❌ Join queue error:", err);
      alert(err.message);
    }
  };

  const leaveQueue = async (restaurantId) => {
    try {
      const res = await fetch("http://localhost:8000/api/leave_queue/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", 
        body: JSON.stringify({
          restaurant: restaurantId,
          name: currentUserName, 
        }),
      });
  
      if (!res.ok) {
        throw new Error("Leave queue failed");
      }
  
      setQueueInfo((prev) => {
        const updated = { ...prev };
        delete updated[restaurantId];
        return updated;
      });

      setNotified(false);
  
    } catch (err) {
      console.error("❌ Leave queue error:", err);
      alert(err.message);
    }
  };

  //SIMULATE RUSH (for testing)
  const simulateRush = async (restaurantId) => {
    try {
      const res = await fetch("http://localhost:8000/api/simulate_rush/", {
        method: "POST",
        credentials: "include", 
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ restaurant: restaurantId }),
      });
  
      if (!res.ok) throw new Error("Rush simulation failed");
  
      alert("🔥 Rush incoming!");
  
    } catch (err) {
      console.error("❌ Simulate rush error:", err);
    }
  };

  //filtering logic
const MAX_DISTANCE = 20;

const filtered = (restaurants || []).filter((r) => {
  const name = (r.name || "").toLowerCase();
  const category = (r.category || "").toLowerCase();

  const matchesSearch = name.includes((searchQuery || "").toLowerCase());

  const matchesFilter =
    filter === "all" ||
    filter === category ||
    (filter === "saved" && saved?.includes(r.id));

    const isNearby =
    r.distance === undefined || r.distance <= MAX_DISTANCE;

  return matchesSearch && matchesFilter && isNearby;
});

const ranked = [...filtered]
  .sort((a, b) => calculateScore(b) - calculateScore(a))
  .slice(0, 3);

  return (
    <div className="app-container">

      {/* TOASTS */}
    <div className="toast-container">
      {notifications.slice(-3).map((n) => (
        <div key={n.id} className="toast">
          {n.message}
        </div>
      ))}
    </div>

      {/* QUEUE BANNER */}
      {Object.keys(queueInfo).length > 0 && (
  <div className="queue-banner">
    {Object.entries(queueInfo).map(([restaurantId, queues]) => {
      const q = queues?.[0];
      if (!q) return null;

      return (
        <div key={restaurantId}>
          <h3>🎟 {q.restaurant}</h3>
          <p>
            {q.status === "waiting"
              ? `${q.position > 0 ? `#${q.position}` : ""} in queue • ⏱ ${q.wait ?? "..."} mins`
              : "🎉 Seated"}
          </p>
        </div>
      );
    })}
  </div>
)}

      <Navbar sortRestaurants={sortRestaurants} setFilter={setFilter} notifications={notifications} />

      <div className="hero">
  <div className="hero-row">
    <img src={logo} alt="Synq Logo" className="hero-logo" />

    <div>
      <h1>Find the best restaurant right now 🍽️</h1>
      <p>Smart recommendations based on wait time, ratings & crowd</p>
    </div>
  </div>
</div>

      <SearchBar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />

      <div className="map-toggle-wrapper">
        <button
          className="menu-btn"
          onClick={() => setShowMap(!showMap)}
        >
          {showMap ? "Hide Map" : "Show Map"}
        </button>
      </div>

      {showMap && restaurants.length > 0 && (
        <MapView restaurants={filtered} userLocation={userLocation} />
      )}

      <div className="filter-row">
        {["all", "italian", "asian", "american", "mexican"].map((type) => (
          <button
            key={type}
            className={`filter-chip ${filter === type ? "active" : ""}`}
            onClick={() => setFilter(type)}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      <div className="smart-section">
        <h2 className="section-title">Smart Picks 🤖</h2>

        <div className="restaurants-grid">
          {ranked.map((r, index) => {
            let tag = "";

            if (index === 0) tag = "🔥 Best Choice";
            else if (index === 1) tag = "🥈 Great Option";
            else if (index === 2) tag = "🥉 Worth Trying";

          return (
            <RestaurantCard
            key={r.id}
            restaurant={r}
            score={calculateScore(r)}
            userLocation={userLocation}
            factors={r.factors}
            mlUsed={r.mlUsed}
            saved={saved}
            toggleSave={toggleSave}
            tag={tag}
            joinQueue={joinQueue}
            leaveQueue={leaveQueue}
            isJoined={!!queueInfo[r.id]}
            simulateRush={() => simulateRush(r.id)}
        />
    );
  })}
</div>
      </div>

      <div className="smart-section">
        <h2 className="section-title">All Restaurants</h2>

        <div className="restaurants-grid">
          {filtered.length > 0 ? (
            filtered.map((r) => (
              <RestaurantCard
                key={r.id}
                restaurant={r}
                userLocation={userLocation}
                score={calculateScore(r)}
                factors={r.factors}
                mlUsed={r.mlUsed}
                saved={saved}
                toggleSave={toggleSave}
                joinQueue={joinQueue}
                leaveQueue={leaveQueue}
                isJoined={!!queueInfo[r.id]}
                simulateRush={() => simulateRush(r.id)}
              />
            ))
          ) : (
            <p style={{ textAlign: "center" }}>
              No restaurants found
            </p>
          )}
        </div>
      </div>

    </div>
  );
}

export default Home;