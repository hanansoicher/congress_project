import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate from React Router
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
`;

const Title = styled.h1`
  color: #004482;
  text-align: center;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
`;

const SearchResultList = styled.ul`
  list-style: none;
  padding: 0;
`;

const SearchResultItem = styled.li`
  padding: 10px;
  margin: 5px 0;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #e0e0e0;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #0066cc;
`;

const ErrorMessage = styled.div`
  color: red;
  text-align: center;
`;

function MembersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate(); // Hook for navigation
  const MAX_RESULTS = 20;

  
  useEffect(() => {
    const fetchSearchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const query = searchQuery ? `?query=${encodeURIComponent(searchQuery)}` : '';
        const response = await fetch(`http://localhost:3001/api/members/search${query}`);
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        const data = await response.json();
        setSearchResults(data.results);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    const delayDebounce = setTimeout(() => {
      fetchSearchResults();
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [searchQuery]);

  const displayedResults = searchResults.slice(0, MAX_RESULTS);

  return (
    <Container>
      <Title>Congress Member Search</Title>
      <SearchInput
        type="text"
        id="scm"
        placeholder="Search Congress members"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      {isLoading && <LoadingMessage>Loading...</LoadingMessage>}
      {error && <ErrorMessage>Error: {error}</ErrorMessage>} 
      <SearchResultList>
        {displayedResults.map((result, index) => (
          <SearchResultItem key={index} onClick={() => navigate(`/members/${result.first_name}-${result.last_name}`)}>
            {`${result.first_name} ${result.last_name}, ${result.state}`}
          </SearchResultItem>
        ))}
        {displayedResults.length === 0 && !isLoading && <SearchResultItem>Enter a search query to find members.</SearchResultItem>}
      </SearchResultList>
    </Container>
  );
}

export default MembersPage;