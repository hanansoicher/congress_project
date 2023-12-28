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
        // Use the query function from your db.jsx file
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

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
