import BackButton from "../components/BackButton";
import RestaurantCard from "../components/RestaurantCard";
import { useEffect, useState } from "react";

function Saved({ saved, toggleSave }) {
  const [restaurants, setRestaurants] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        // Fetch all restaurants
        const res = await fetch("http://localhost:8000/api/restaurants/");
        const data = await res.json();

        // Enrich with wait time + ML data (same as Home)
        const enriched = await Promise.all(
          data.map(async (r) => {
            try {
              const waitRes = await fetch(
                `http://localhost:8000/api/predict-wait/${r.id}/`
              );
              const waitData = await waitRes.json();

              return {
                ...r,
                wait_time: waitData.wait_time,
                confidence: waitData.confidence,
                factors: waitData.factors,
                mlUsed: waitData.ml_used,

                // keep consistent with Home styling
                distance: Math.random() * 5,
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

        setRestaurants(enriched);
      } catch (err) {
        console.error(err);
      }
    }

    loadData();
  }, []);

  const savedRestaurants = restaurants.filter((r) =>
    saved.includes(Number(r.id))
  );

  return (
    <div className="app-container">
      <BackButton />

      <div className="header">
        <h1 className="app-title">Synq</h1>
        <p className="tagline">YOUR SAVED RESTAURANTS</p>
      </div>

      <div className="restaurants-grid">
        {savedRestaurants.length > 0 ? (
          savedRestaurants.map((r) => (
            <RestaurantCard
              key={r.id}
              restaurant={r}
              factors={r.factors}
              mlUsed={r.mlUsed}
              saved={saved}
              toggleSave={toggleSave}
            />
          ))
        ) : (
          <p style={{ textAlign: "center" }}>
            No saved restaurants yet ❤️
          </p>
        )}
      </div>
    </div>
  );
}

export default Saved;

