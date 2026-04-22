import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

function StaffDashboard() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [tables, setTables] = useState([]);
  const [queue, setQueue] = useState([]);
  const [waitTime, setWaitTime] = useState(0);
  const [loading, setLoading] = useState(true);

  // ---------------- FETCH DASHBOARD ----------------
  const fetchDashboard = async () => {
    try {
      setLoading(true);
  
      const res = await fetch(
        `http://localhost:8000/api/staff/${id}/`,
        {
          credentials: "include",
        }
      );
  
      if (res.status === 401) {
        console.log("❌ Not logged in");
        navigate("/staff-login");
        return;
      }
      
      if (res.status === 403) {
        console.log("❌ Forbidden (wrong role or restaurant)");
        navigate("/staff-login");
        return;
      }
      
      if (!res.ok) throw new Error("Failed to fetch dashboard");
  
      const data = await res.json();
      console.log("QUEUE DATA:", data.queue);
  
      console.log("✅ Dashboard:", data);
  
      setTables(data.tables || []);
      setQueue(Array.isArray(data.queue) ? data.queue : []);
      setWaitTime(data.wait_time || 0);
  
    } catch (err) {
      console.error("❌ Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ---------------- REAL-TIME + POLLING ----------------
  useEffect(() => {
    if (!id) return;
  
    fetchDashboard();
  
    // Polling (fallback)
    const interval = setInterval(fetchDashboard, 30000);
  
    // WebSocket (REAL-TIME)
    const socket = new WebSocket("ws://localhost:8000/ws/queue/");

socket.onopen = () => {
  console.log("✅ WebSocket connected");
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);

  console.log("🔥 WS DATA:", data);

  if (data.restaurant_id && parseInt(id) === data.restaurant_id) {
    // DIRECT UPDATE (no delay)
    if (data.queue) setQueue(data.queue);
    if (data.tables) setTables(data.tables);
    if (data.wait_time !== undefined) setWaitTime(data.wait_time);
  }
};

socket.onclose = () => {
  console.log("❌ WebSocket closed");
};

socket.onerror = (err) => {
  console.error("❌ WebSocket error:", err);
};
  
    return () => {
      clearInterval(interval);
      socket.close();
    };
  
  }, [id]);

  // ---------------- UPDATE TABLE ----------------
  const handleChange = async (tableId, value) => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/update_table_status/${tableId}/`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ status: value.toUpperCase() }),
        }
      );
  
      if (!res.ok) throw new Error("Failed to update");
  
      const data = await res.json();
  
      // INSTANT wait time update
      if (data.wait_time !== undefined) {
        setWaitTime(data.wait_time);
      }
      
      // small delay prevents overwrite race
      setTimeout(fetchDashboard, 300);
  
    } catch (err) {
      console.error("❌ Update error:", err);
    }
  };

  // ---------------- BILLING ----------------
  const handleBilling = async (tableId) => {
    try {
      const res = await fetch(
        "http://localhost:8000/api/billing/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ table_id: tableId }),
        }
      );

      if (!res.ok) throw new Error("Billing failed");

      await fetchDashboard();

    } catch (err) {
      console.error("❌ Billing error:", err);
    }
  };

  // ---------------- SEAT CUSTOMER ----------------
  const seatCustomer = async (queueId) => {
    try {
      const res = await fetch(
        "http://localhost:8000/api/seat/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ queue_id: queueId }),
        }
      );

      if (!res.ok) throw new Error("Seat failed");

      await fetchDashboard();

    } catch (err) {
      console.error("❌ Seat error:", err);
    }
  };

  // ---------------- UI ----------------
  return (
    <div className="login-page">

      <button className="back-btn" onClick={() => navigate("/")}>
        ← Logout
      </button>

      <div className="login-header">
        <h1 className="app-title">Synq</h1>
        <p className="tagline">STAFF DASHBOARD</p>
      </div>

      <div className="profile-card">

        <h2>Table Management Panel</h2>
        <div className="card-divider" />

        {loading ? (
          <p>Loading...</p>
        ) : tables.length === 0 ? (
          <p>No tables found ⚠️</p>
        ) : (
          <div className="table-list">
            {tables.map((t) => (
              <div key={t.id} className="table-row">
                <span>🪑 Table {t.table_number || t.id}</span>

                <select
                  value={t.status}
                  onChange={(e) =>
                    handleChange(t.id, e.target.value)
                  }
                >
                  <option value="FREE">🟢 Free</option>
                  <option value="OCCUPIED">🔴 Occupied</option>
                  <option value="RESERVED">🟡 Reserved</option>
                </select>

                {t.status === "OCCUPIED" && (
                  <button
                    className="bill-btn"
                    onClick={() => handleBilling(t.id)}
                  >
                    Generate Bill
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="wait-badge big">
          {waitTime} MIN WAIT
        </div>

        <h3 className="section-title">🔥 Live Queue</h3>

        {!Array.isArray(queue) || queue.length === 0 ? (
            <p className="empty-text">No customers waiting</p>
          ) : (
          <div className="queue-container">
            {queue.map((q) => (
              <div key={q.id} className="queue-card">

                <div className="queue-left">
                  <span className="queue-position">#{q.position}</span>
                  <div>
                    <p className="queue-name">{q.name}</p>
                    <p className="queue-size">{q.party_size} people</p>
                  </div>
                </div>

                <button
                  className="seat-btn"
                  onClick={() => seatCustomer(q.id)}
                >
                  Seat
                </button>

              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default StaffDashboard;