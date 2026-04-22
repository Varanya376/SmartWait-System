function FilterChips({ filter, setFilter }) {

    const cuisines = ["all", "italian", "asian", "american", "mexican"]
  
    return (
      <div className="filter-chips">
  
        {cuisines.map((c) => (
          <button
            key={c}
            className={`chip ${filter === c ? "active" : ""}`}
            onClick={() => setFilter(c)}
          >
            {c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
  
      </div>
    )
  }
  
  export default FilterChips