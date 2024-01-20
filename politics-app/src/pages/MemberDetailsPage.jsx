import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';

const DetailsContainer = styled.div`
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
`;

const MemberImage = styled.img`
  width: 100%;
  max-width: 300px;
  height: auto;
  display: block;
  margin: 0 auto;
`;

const SectionTitle = styled.h2`
  color: #004482;
  margin-top: 20px;
`;

const TextContent = styled.p`
  line-height: 1.6;
`;

const List = styled.ul`
  list-style: none;
  padding: 0;
`;

const ListItem = styled.li`
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 4px;
`;

// eslint-disable-next-line no-unused-vars
const SubSectionTitle = styled.h3`
  color: #003366;
  margin-top: 15px;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #0066cc;
`;

const ErrorMessage = styled.div`
  color: red;
  text-align: center;
`;

function MemberDetailsPage() {
    const [memberProfile, setMemberProfile] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const { memberName } = useParams();
  
    useEffect(() => {
      if (memberName) {
        const [firstName, lastName] = memberName.split('-');
        const queryName = `${firstName}${lastName}`;
  
        fetch(`http://localhost:3001/api/members/profile/${queryName}`)
          .then(response => {
            if (!response.ok) {
              throw new Error(`Error: ${response.status}`);
            }
            return response.json();
          })
          .then(data => {
            setMemberProfile(data);
            setIsLoading(false);
          })
          .catch(error => {
            setError(error.message);
            setIsLoading(false);
          });
      }
    }, [memberName]);
  
    if (isLoading) return <LoadingMessage>Loading...</LoadingMessage>;
    if (error) return <ErrorMessage>Error: {error}</ErrorMessage>;
    if (!memberProfile) return <ErrorMessage>No member found</ErrorMessage>;
  
    const { details, roles, committees, subcommittees, billsSponsored, votes, statements } = memberProfile;
  
    return (
      <DetailsContainer>
        {details.picture && <MemberImage src={details.picture} alt={`${details.first_name} ${details.last_name}`} />}
        <SectionTitle>Biography</SectionTitle>
        <TextContent>{details.biography}</TextContent>
        
        {/* Other member details can be added here */}
        
        <SectionTitle>Roles</SectionTitle>
        <List>
          {roles.map(role => (
            <ListItem key={role.id}>{role.title}, {role.congress}</ListItem>
          ))}
        </List>
  
        <SectionTitle>Committees</SectionTitle>
        <List>
          {committees.map(committee => (
            <ListItem key={committee.committee_id}>{committee.name}</ListItem>
          ))}
        </List>
  
        <SectionTitle>Subcommittees</SectionTitle>
        <List>
          {subcommittees.map(subcommittee => (
            <ListItem key={subcommittee.subcommittee_id}>{subcommittee.name}</ListItem>
          ))}
        </List>
  
        <SectionTitle>Bills Sponsored</SectionTitle>
        <List>
          {billsSponsored.map(bill => (
            <ListItem key={bill.bill_id}>{bill.title}</ListItem>
          ))}
        </List>
  
        <SectionTitle>Voting Record</SectionTitle>
        <List>
          {votes.map(vote => (
            <ListItem key={vote.vote_id}>{vote.description}, Position: {vote.vote_position}</ListItem>
          ))}
        </List>
  
        <SectionTitle>Public Statements</SectionTitle>
        <List>
          {statements.map(statement => (
            <ListItem key={statement.statement_id}>{statement.title}, Date: {statement.date}</ListItem>
          ))}
        </List>
      </DetailsContainer>
    );
  }
  
  export default MemberDetailsPage;