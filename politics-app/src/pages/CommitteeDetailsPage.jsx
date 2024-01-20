import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';

const PageContainer = styled.div`
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f4f4;
`;

const Title = styled.h1`
  color: #004482;
  text-align: center;
  font-size: 2.5rem;
`;

const Section = styled.section`
  margin-top: 20px;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
`;

const SectionTitle = styled.h2`
  color: #0056b3;
  margin-bottom: 10px;
`;

const List = styled.ul`
  list-style: none;
  padding: 0;
  max-height: 300px; // Set a maximum height
  overflow-y: auto; // Enable vertical scrolling
`;

const ListItem = styled.li`
  margin-bottom: 10px;
`;

const CommitteeInfo = styled.div`
  background-color: #e6f7ff;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
`;

const ExternalLink = styled.a`
  color: #0066cc;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #0066cc;
  font-size: 1.2rem;
`;

const CommitteeDetailsPage = () => {
  const { committeeId } = useParams();
  const [committeeDetails, setCommitteeDetails] = useState(null);
  const [committeeMembers, setCommitteeMembers] = useState([]);
  const [recentBills, setRecentBills] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        // Fetch committee details
        const detailsResponse = await fetch(`/api/committees/details/${committeeId}`);
        if (!detailsResponse.ok) throw new Error('Error fetching committee details');
        const detailsData = await detailsResponse.json();
        setCommitteeDetails(detailsData.committee);

        // Fetch committee members
        const membersResponse = await fetch(`/api/committees/members/${committeeId}`);
        if (!membersResponse.ok) throw new Error('Error fetching committee members');
        const membersData = await membersResponse.json();
        setCommitteeMembers(membersData.members);

        // Fetch recent bills
        const billsResponse = await fetch(`/api/committees/bills/${committeeId}`);
        if (!billsResponse.ok) throw new Error('Error fetching recent bills');
        const billsData = await billsResponse.json();
        setRecentBills(billsData.bills);

        setIsLoading(false);
      } catch (err) {
        setError(err.message);
        setIsLoading(false);
      }
    };

    fetchDetails();
  }, [committeeId]);

  if (isLoading) {
    return <LoadingMessage>Loading...</LoadingMessage>;
  }

  return (
    <PageContainer>
      <Title>Committee Details</Title>

      {committeeDetails && (
        <CommitteeInfo>
          <SectionTitle>{committeeDetails.name}</SectionTitle>
          <p>Chamber: {committeeDetails.chamber}</p>
          <p>URL: <ExternalLink href={committeeDetails.url} target="_blank" rel="noopener noreferrer">{committeeDetails.url}</ExternalLink></p>
        </CommitteeInfo>
      )}

      <Section>
        <SectionTitle>Current Members</SectionTitle>
        {committeeMembers.length > 0 ? (
          <List>
            {committeeMembers.map((member, index) => (
              <ListItem key={member.member_id + '-' + index}>{member.first_name} {member.last_name}</ListItem>
            ))}
          </List>
        ) : <p>No members available.</p>}
      </Section>

      <Section>
        <SectionTitle>Recent Bills</SectionTitle>
        {recentBills.length > 0 ? (
          <List>
            {recentBills.map(bill => (
              <ListItem key={bill.bill_id}>{bill.title}</ListItem>
            ))}
          </List>
        ) : <p>No recent bills available.</p>}
      </Section>
    </PageContainer>
  );
};

export default CommitteeDetailsPage;