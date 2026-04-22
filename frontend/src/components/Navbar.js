import { useState } from "react";
import logo from "../assets/synq-logo.png";
import FilterMenu from "./FilterMenu";

function Navbar({ sortRestaurants, setFilter }) {
  const [open, setOpen] = useState(false);

  return (
    <header className="navbar">
  
      {/* LEFT → LOGO */}
      <div className="navbar-left">
        <img src={logo} alt="Synq Logo" className="nav-logo" />
      </div>
  
      {/* RIGHT → MENU */}
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

    </header>
  );
}

export default Navbar;