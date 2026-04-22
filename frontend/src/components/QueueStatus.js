function QueueStatus({ wait, crowd }) {

    const totalBars = 5;
  
    // Normalization (handles all formats)
    let normalized;
  
    if (crowd <= 1) {
      normalized = crowd;            // already 0–1
    } else if (crowd <= 5) {
      normalized = crowd / 5;        // scale 1–5 → 0–1
    } else {
      normalized = crowd / 100;      // scale 0–100 → 0–1
    }
  
    const filledBars = Math.round(normalized * totalBars);
  
    return (
      <div>
  
        {/* WAIT BADGE */}
        <div className="wait-badge">
          {wait} MIN WAIT
        </div>
  
        {/* CROWD LEVEL INLINE */}
        <div className="crowd-row">
  
          <p className="crowd-label">
            Crowd Level
          </p>
  
          <div className="crowd-bars">
            {[...Array(totalBars)].map((_, i) => (
              <span
                key={i}
                className={`bar ${i < filledBars ? "active" : ""}`}
              />
            ))}
          </div>
  
        </div>
  
      </div>
    );
  }
  
  export default QueueStatus;