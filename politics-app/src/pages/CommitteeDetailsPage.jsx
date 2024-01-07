import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

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
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Committee Details</h1>
      {committeeDetails && (
        <div>
          <h2>{committeeDetails.name}</h2>
          <p>Chamber: {committeeDetails.chamber}</p>
          <p>URL: <a href={committeeDetails.url}>{committeeDetails.url}</a></p>
        </div>
      )}

      <section>
        <h2>Current Members</h2>
        {committeeMembers.length > 0 ? (
            <ul>
            {committeeMembers.map((member, index) => (
                <li key={member.member_id + '-' + index}>{member.first_name} {member.last_name}</li>
            ))}
            </ul>
        ) : <p>No members available.</p>}
      </section>

      <section>
        <h2>Recent Bills</h2>
        {recentBills.length > 0 ? (
          <ul>
            {recentBills.map(bill => (
              <li key={bill.bill_id}>{bill.title}</li>
            ))}
          </ul>
        ) : <p>No recent bills available.</p>}
      </section>
    </div>
  );
};

export default CommitteeDetailsPage;
