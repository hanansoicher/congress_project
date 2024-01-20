import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';


const PageContainer = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f4f4;
`;

const Title = styled.h1`
  color: #004482;
  text-align: center;
  font-size: 2.5rem;
`;

const CommitteesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: auto auto;
  gap: 20px;
  margin-top: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const CommitteeSection = styled.section`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  padding: 20px;
  max-height: 300px; // Set a maximum height
  overflow-y: auto; // Enable vertical scrolling
  grid-column: span 1;

  &:last-child {
    grid-column: 1 / -1; // Makes Joint Committees span full width
  }
`;

const SectionTitle = styled.h2`
  color: #0056b3;
  margin-bottom: 15px;
`;

const StyledLink = styled(Link)`
  display: block;
  padding: 10px 0;
  font-size: 1rem;
  font-weight: bold;
  color: #0066cc;
  text-decoration: none;
  border-bottom: 1px solid #f0f0f0;

  &:hover {
    background-color: #e6f7ff;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #0066cc;
  font-size: 1.2rem;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 10px;
  margin: 20px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
`;

const CommitteesPage = () => {
    const [houseCommittees, setHouseCommittees] = useState([]);
    const [senateCommittees, setSenateCommittees] = useState([]);
    const [jointCommittees, setJointCommittees] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    // eslint-disable-next-line no-unused-vars
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCommittees = async (chamber) => {
            try {
                const response = await fetch(`/api/committees/${chamber}`);
                const text = await response.text(); // Read the response as text first
        
                try {
                    const data = JSON.parse(text); // Try to parse it as JSON
                    return data.committees;
                } catch (jsonError) {
                    console.error('Response is not valid JSON:', text);
                    throw new Error(`Response parsing error for chamber ${chamber}: ${jsonError.message}`);
                }
            } catch (err) {
                console.error('Fetch error for chamber', chamber, err);
                setError(err.message);
                return []; // Return empty array on error
            }
        };
        

        const loadCommittees = async () => {
            setIsLoading(true);
            const houseData = await fetchCommittees('house');
            setHouseCommittees(houseData);

            const senateData = await fetchCommittees('senate');
            setSenateCommittees(senateData);

            const jointData = await fetchCommittees('joint');
            setJointCommittees(jointData);

            setIsLoading(false);
        };

        loadCommittees();
    }, []);




    const filterCommittees = (committees) => {
        return committees.filter(committee =>
            committee.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
    };

    const filteredHouseCommittees = filterCommittees(houseCommittees);
    const filteredSenateCommittees = filterCommittees(senateCommittees);
    const filteredJointCommittees = filterCommittees(jointCommittees);

    if (isLoading) {
        return <LoadingMessage>Loading...</LoadingMessage>;
    }

    return (
        <PageContainer>
            <Title>Committees Page</Title>

            <SearchInput
                type="text"
                placeholder="Search for committees..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />

            <CommitteesGrid>
                <CommitteeSection>
                    <SectionTitle>House Committees</SectionTitle>
                    {filteredHouseCommittees.map(committee => (
                        <StyledLink key={committee.committee_id} to={`/committees/${committee.committee_id}`}>
                            {committee.name}
                        </StyledLink>
                    ))}
                </CommitteeSection>

                <CommitteeSection>
                    <SectionTitle>Senate Committees</SectionTitle>
                    {filteredSenateCommittees.map(committee => (
                        <StyledLink key={committee.committee_id} to={`/committees/${committee.committee_id}`}>
                            {committee.name}
                        </StyledLink>
                    ))}
                </CommitteeSection>

                <CommitteeSection>
                    <SectionTitle>Joint Committees</SectionTitle>
                    {filteredJointCommittees.map(committee => (
                        <StyledLink key={committee.committee_id} to={`/committees/${committee.committee_id}`}>
                            {committee.name}
                        </StyledLink>
                    ))}
                </CommitteeSection>
            </CommitteesGrid>
        </PageContainer>
    );
};

export default CommitteesPage;