import { useState } from "react";
import logo from "../assets/synq-logo.png";
import FilterMenu from "./FilterMenu";

function Navbar({ sortRestaurants, setFilter, notifications = [] }) {
  const [open, setOpen] = useState(false);

  return (
    <header className="navbar">
  
      {/* RIGHT → ACTIONS */}
      <div className="nav-actions">

        {/* 🔔 Notification Bell */}
        <div className="bell">
          🔔
          {notifications.length > 0 && (
            <span className="badge">{notifications.length}</span>
          )}
        </div>

        {/* ⋮ MENU */}
        <div className="kebab-wrapper">
          <button
            className="kebab-btn"
            onClick={() => setOpen(!open)}
          >
            ⋮
          </button>

          {open && (
            <div className="menu-container">
              <FilterMenu
                sortRestaurants={sortRestaurants}
                setFilter={setFilter}
                closeMenu={() => setOpen(false)}
              />
            </div>
          )}
        </div>

      </div>

    </header>
  );
}

export default Navbar;