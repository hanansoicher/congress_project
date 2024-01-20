import os
import psycopg2
import requests
from datetime import datetime

# Database connection function
def connect_to_db():
    db_conn_info = {
        'host': 'localhost',
        'port': '5433',
        'dbname': 'politics_db',
        'user': 'postgres',
        'password': 'Ignorantbliss(9)',
        'sslmode': 'prefer',
        'connect_timeout': 10
    }
    return psycopg2.connect(**db_conn_info)

# Fetch Statements
def fetch_statements(api_key, endpoint, offset=0):
    url = f"https://api.propublica.org/congress/v1/statements/{endpoint}.json?offset={offset}"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error fetching statements: Status code {response.status_code}")
        return []

# Function to insert congressional statements
def insert_congressional_statements(cursor, statements):
    for statement in statements:
        insert_query = """
        INSERT INTO congressional_statements (statement_id, title, date, url, member_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (statement_id) DO NOTHING;
        """
        params = (
            statement['statement_id'],
            statement['title'],
            statement['date'],
            statement['url'],
            statement['member_id']
        )
        cursor.execute(insert_query, params)
        print(f"Inserted Congressional Statement: {statement['title']}")

# Function to insert committee statements
def insert_committee_statements(cursor, statements):
    for statement in statements:
        insert_query = """
        INSERT INTO committee_statements (statement_id, title, date, url, committee_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (statement_id) DO NOTHING;
        """
        params = (
            statement['statement_id'],
            statement['title'],
            statement['date'],
            statement['url'],
            statement['committee_id']
        )
        cursor.execute(insert_query, params)
        print(f"Inserted Committee Statement: {statement['title']}")

# Main function
def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        # Process Congressional Statements
        offset = 0
        while True:
            statements = fetch_statements(api_key, 'latest', offset)
            if not statements:
                break
            insert_congressional_statements(cur, statements)
            conn.commit()
            offset += 20

        # Process Committee Statements
        offset = 0
        while True:
            statements = fetch_statements(api_key, 'committees/latest', offset)
            if not statements:
                break
            insert_committee_statements(cur, statements)
            conn.commit()
            offset += 20

    except Exception as e:
        print(f"Error in main process: {e}")
        conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
