import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'politics_db',
    password: 'Ignorantbliss(9)',
    port: '5433',
});

export function query(text, params) { return pool.query(text, params); }
