import express from 'express';
import cors from 'cors';
import { query } from './db.js';
import 'dotenv/config';

const app = express();

const port = 3001;

app.use(cors()); // Enable CORS for your front-end



app.get('/api/members/search', async (req, res) => {
    const { query: searchText } = req.query; // Use searchText as the query

    try {
        const result = await query(
            "SELECT * FROM members WHERE first_name ILIKE $1 OR middle_name ILIKE $1 OR last_name ILIKE $1",
            [`%${searchText}%`]
        );

        res.json({ results: result.rows });
    } catch (error) {
        console.error('Error searching members:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/committees/:chamber', async (req, res) => {
    const { chamber } = req.params;

    try {
        const result = await query(
            "SELECT * FROM committees WHERE chamber = $1",
            [chamber]
        );

        res.json({ committees: result.rows });
    } catch (error) {
        console.error('Error fetching committees:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/committees/details/:committeeId', async (req, res) => {
    const { committeeId } = req.params;

    try {
        const result = await query("SELECT * FROM committees WHERE committee_id = $1", [committeeId]);
        res.json({ committee: result.rows[0] || null });
    } catch (error) {
        console.error('Error fetching committee details:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/committees/members/:committeeId', async (req, res) => {
    const { committeeId } = req.params;

    try {
        const result = await query(
            "SELECT m.* FROM members m JOIN committee_members cm ON m.member_id = cm.member_id WHERE cm.committee_id = $1",
            [committeeId]
        );
        res.json({ members: result.rows });
    } catch (error) {
        console.error('Error fetching committee members:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/committees/bills/:committeeId', async (req, res) => {
    const { committeeId } = req.params;

    try {
        const result = await query(
            "SELECT * FROM bills b JOIN bill_committees bc ON b.bill_id = bc.bill_id WHERE bc.committee_code = $1 ORDER BY b.introduced_date DESC LIMIT 10",
            [committeeId]
        );
        res.json({ bills: result.rows });
    } catch (error) {
        console.error('Error fetching bills:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});


app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
