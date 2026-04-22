function SearchBar({ searchQuery, setSearchQuery }) {
    return (
      <div className="search-container">
  
        <div className="search-wrapper">
          <span className="search-icon">🔍</span>
  
          <input
            className="search-input"
            placeholder="Search restaurants..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
  
      </div>
    );
  }

export default SearchBar;