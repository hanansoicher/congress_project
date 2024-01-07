import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const CommitteesPage = () => {
    const [houseCommittees, setHouseCommittees] = useState([]);
    const [senateCommittees, setSenateCommittees] = useState([]);
    const [jointCommittees, setJointCommittees] = useState([]);
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

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Committees Page</h1>

            <h2>House Committees</h2>
            <ul>
                {houseCommittees.map(committee => (
                    <li key={committee.committee_id}>
                        <Link to={`/committees/${committee.committee_id}`}>{committee.name}</Link>
                    </li>
                ))}
            </ul>

            <h2>Senate Committees</h2>
            <ul>
                {senateCommittees.map(committee => (
                    <li key={committee.committee_id}>
                        <Link to={`/committees/${committee.committee_id}`}>{committee.name}</Link>
                    </li>
                ))}
            </ul>

            <h2>Joint Committees</h2>
            <ul>
                {jointCommittees.map(committee => (
                    <li key={committee.committee_id}>
                        <Link to={`/committees/${committee.committee_id}`}>{committee.name}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default CommitteesPage;
