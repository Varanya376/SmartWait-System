import BackButton from "../components/BackButton";
import RestaurantCard from "../components/RestaurantCard";
import { useEffect, useState } from "react";

function Saved({ saved, toggleSave }) {
  const [restaurants, setRestaurants] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/restaurants/")
      .then((res) => res.json())
      .then((data) => {
        setRestaurants(data);
      })
      .catch((err) => console.error(err));
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
              restaurant={{
                ...r,
                distance: Math.random() * 5,
                rating: Number((Math.random() * 2 + 3).toFixed(1)),
                crowd: Math.floor(Math.random() * 5) + 1,
              }}
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