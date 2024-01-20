import { useState, useEffect } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: 2rem;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  margin: auto;
`;

const Title = styled.h2`
  color: #333;
`;

const CheckboxLabel = styled.label`
  display: block;
  margin-bottom: 0.5rem;
`;

const Select = styled.select`
  margin: 1rem 0;
  padding: 0.5rem;
`;

const Button = styled.button`
  padding: 0.5rem 1rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 1rem;

  &:hover {
    background-color: #3a78d2;
  }
`;

const Questionnaire = () => {
    const [committees, setCommittees] = useState([]);
    const [selectedCommittees, setSelectedCommittees] = useState([]);
    const [selectedParty, setSelectedParty] = useState('');
    const [selectedMembers, setSelectedMembers] = useState([]);
    const [selectedState, setSelectedState] = useState('');
    // Add states list
    const states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas',
        'California', 'Colorado', 'Connecticut', 'Delaware',
        'Florida', 'Georgia', 'Hawaii', 'Idaho',
        'Illinois', 'Indiana', 'Iowa', 'Kansas',
        'Kentucky', 'Louisiana', 'Maine', 'Maryland',
        'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
        'Missouri', 'Montana', 'Nebraska', 'Nevada',
        'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
        'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma',
        'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
        'South Dakota', 'Tennessee', 'Texas', 'Utah',
        'Vermont', 'Virginia', 'Washington', 'West Virginia',
        'Wisconsin', 'Wyoming'
    ];
    
  
    const [congressMembers, setCongressMembers] = useState([]);

    const fetchCongressMembers = async () => {
      try {
        const response = await fetch('/api/members/current');
        const data = await response.json();
        setCongressMembers(data); 
      } catch (error) {
        console.error('Error fetching congress members:', error);
      }
    };

useEffect(() => {
    fetchCommittees();
    fetchCongressMembers();
}, []);

  const fetchCommittees = async () => {
    try {
      const response = await fetch('/api/committees'); // Replace with your backend API endpoint
      const data = await response.json();
      setCommittees(data);
    } catch (error) {
      console.error('Error fetching committees:', error);
    }
  };

  const handleCommitteeChange = (e) => {
    const { value, checked } = e.target;
    setSelectedCommittees((prev) =>
      checked ? [...prev, value] : prev.filter((item) => item !== value)
    );
  };

  const handleMemberChange = (e) => {
    const { value, checked } = e.target;
    setSelectedMembers((prev) =>
      checked ? [...prev, value] : prev.filter((memberId) => memberId !== value)
    );
  };

  const handleSubmit = () => {
    // Logic to handle the submission of the questionnaire
    // This could involve sending data to a backend server
    console.log({
      selectedCommittees,
      selectedParty,
      selectedMembers,
      selectedState
    });
  };

  return (
    <Container>
      <Title>Customize Your Experience</Title>

      {/* Party selection */}
      <div>
        <Title>Which party do you identify with?</Title>
        <Select value={selectedParty} onChange={(e) => setSelectedParty(e.target.value)}>
          <option value="">Select a Party</option>
          <option value="democrat">Democrat</option>
          <option value="republican">Republican</option>
          <option value="independent">Independent</option>
        </Select>
      </div>

      {/* Committees selection */}
      <div>
        <Title>What committees do you care about?</Title>
        {committees.map((committee) => (
          <CheckboxLabel key={committee.id}>
            <input
              type="checkbox"
              value={committee.name}
              onChange={handleCommitteeChange}
            />
            {committee.name}
          </CheckboxLabel>
        ))}
      </div>

      <div>
        <Title>Which Congress members would you like to follow?</Title>
        {congressMembers.map((member) => (
          <CheckboxLabel key={member.id}>
            <input
              type="checkbox"
              value={member.id}
              checked={selectedMembers.includes(member.id)}
              onChange={handleMemberChange}
            />
            {`${member.first_name} ${member.middle_name ? member.middle_name + ' ' : ''}${member.last_name}`}
          </CheckboxLabel>
        ))}
      </div>

      {/* State selection */}
      <div>
        <Title>What state do you live in?</Title>
        <Select value={selectedState} onChange={(e) => setSelectedState(e.target.value)}>
          <option value="">Select a State</option>
          {states.map((state) => (
            <option value={state} key={state}>{state}</option>
          ))}
        </Select>
      </div>

      <Button onClick={handleSubmit}>Submit Preferences</Button>
    </Container>
  );
};

export default Questionnaire;
