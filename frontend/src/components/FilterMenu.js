import { useNavigate } from "react-router-dom";

function FilterMenu({ sortRestaurants, closeMenu }) {

  const navigate = useNavigate();

  return (
    <div className="filter-menu">

      {/* SORT OPTIONS */}
      <div
        className="detail-item"
        onClick={() => {
          sortRestaurants("wait");
          closeMenu();
        }}
      >
        ⏱ Shortest Wait
      </div>

      <div
        className="detail-item"
        onClick={() => {
          sortRestaurants("rating");
          closeMenu();
        }}
      >
        ⭐ Highest Rating
      </div>

      <div
        className="detail-item"
        onClick={() => {
          sortRestaurants("distance");
          closeMenu();
        }}
      >
        📍 Nearest
      </div>

      <div className="divider"></div>

      {/* SAVED PAGE */}
      <div
        className="detail-item"
        onClick={() => {
          navigate("/saved");
          closeMenu();
        }}
      >
        ❤️ Saved Restaurants
      </div>

      <div className="divider"></div>

      {/* PROFILE PAGE (FIXED) */}
      <div
        className="detail-item"
        onClick={() => {
          navigate("/profile");
          closeMenu();
        }}
      >
        👤 Profile
      </div>

      {/* LOGOUT */}
      <div
        className="detail-item"
        onClick={() => {
          // optional: clear auth/localStorage later
          navigate("/");
          closeMenu();
        }}
      >
        🚪 Log out
      </div>

    </div>
  );
}

export default FilterMenu;