import express from 'express';
import cors from 'cors';
import { query } from './db.js';
import 'dotenv/config';

const app = express();
const port = 3001;
app.use(cors()); 

app.get('/api/members/current', async (req, res) => {
    try {
        const result = await query(
            "SELECT * FROM members WHERE in_office = true"
        );
        res.json({ members: result.rows });
    } catch (error) {
        console.error('Error fetching current members:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/members/profile/:memberId', async (req, res) => {
    const { memberId } = req.params;

    try {
        const memberDetails = await query("SELECT * FROM members WHERE member_id = $1", [memberId]);
        const memberRoles = await query("SELECT * FROM member_roles WHERE member_id = $1", [memberId]);
        const memberCommittees = await query("SELECT c.* FROM committees c JOIN committee_members cm ON c.committee_id = cm.committee_id WHERE cm.member_id = $1", [memberId]);
        const memberSubcommittees = await query("SELECT s.* FROM subcommittees s JOIN member_subcommittees ms ON s.subcommittee_id = ms.subcommittee_id WHERE ms.member_id = $1", [memberId]);
        const sponsoredBills = await query("SELECT * FROM bills WHERE sponsor_id = $1", [memberId]);
        const memberVotes = await query("SELECT v.*, mv.vote_position FROM votes v JOIN member_votes mv ON v.vote_id = mv.vote_id WHERE mv.member_id = $1", [memberId]);
        const memberStatements = await query("SELECT * FROM congressional_statements WHERE member_id = $1", [memberId]);

        res.json({
            details: memberDetails.rows[0] || null,
            roles: memberRoles.rows,
            committees: memberCommittees.rows,
            subcommittees: memberSubcommittees.rows,
            billsSponsored: sponsoredBills.rows,
            votes: memberVotes.rows,
            statements: memberStatements.rows
        });
    } catch (error) {
        console.error('Error fetching member profile:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});


app.get('/api/members/search', async (req, res) => {
    const { query: searchText } = req.query;

    try {
        const result = await query(
            "SELECT * FROM members WHERE first_name ILIKE $1 OR middle_name ILIKE $1 OR last_name ILIKE $1", [`%${searchText}%`]);
        res.json({ results: result.rows });
    } catch (error) {
        console.error('Error searching members:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/committees', async (req, res) => {

    try {
        const result = await query(
            "SELECT * FROM committees"
        );
        res.json({ committees: result.rows });
    } catch (error) {
        console.error('Error fetching committees:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/api/committees/:chamber', async (req, res) => {
    const { chamber } = req.params;

    try {
        const result = await query(
            "SELECT * FROM committees WHERE chamber = $1", [chamber]);
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
            "SELECT m.* FROM members m JOIN committee_members cm ON m.member_id = cm.member_id WHERE cm.committee_id = $1", [committeeId]);
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
