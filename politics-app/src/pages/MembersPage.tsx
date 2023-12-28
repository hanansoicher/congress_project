import React, { useState } from 'react';
import '../styles/MembersPage.css';

interface SearchResult {
  first_name: string;
  last_name: string;
  state: string;
}

function MembersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const MAX_RESULTS = 20;

  const handleSearch = async () => {
    if (!searchQuery) {
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:3001/api/members/search?query=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      setSearchResults(data.results);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  const displayedResults = searchResults.slice(0, MAX_RESULTS);

  return (
    <div>
      <h1>Congress Member Search</h1>
      <input
        type="text"
        id="scm"
        placeholder="Search Congress members"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>
      {isLoading && <div>Loading...</div>}
      {error && <div>Error: {(error as Error).message}</div>}
      <ul className="scrollable-results">
        {displayedResults.map((result, index) => (
          <li key={index}>
            {`${result.first_name} ${result.last_name}, ${result.state}`}
          </li>
        ))}
        {displayedResults.length === 0 && !isLoading && <li>No results found.</li>}
      </ul>
    </div>
  );
}

export default MembersPage;