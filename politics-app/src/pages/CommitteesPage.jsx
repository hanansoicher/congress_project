// eslint-disable-next-line no-unused-vars
import React, { useEffect, useState } from 'react';

const CommitteesPage = () => {
    const [committees, setCommittees] = useState([]);

    useEffect(() => {
        // Fetch committees data from the database
        const fetchCommittees = async () => {
            try {
                const response = await fetch('/api/committees'); // Replace with your API endpoint
                const data = await response.json();
                setCommittees(data);
            } catch (error) {
                console.error('Error fetching committees:', error);
            }
        };

        fetchCommittees();
    }, []);

    return (
        <div>
            <h1>Committees Page</h1>
            {committees.map(committee => (
                <div key={committee.id}>
                    <h2>{committee.name}</h2>
                    <div>
                        {committee.members.map(member => (
                            <div key={member.id}>
                                <p>{member.name}</p>
                                {/* Add more member details here */}
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default CommitteesPage;
