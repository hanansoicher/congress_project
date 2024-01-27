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
    print("Connecting to the database...")
    return psycopg2.connect(**db_conn_info)

def fetch_statements(api_key, endpoint, offset=0):
    url = f"https://api.propublica.org/congress/v1/statements/{endpoint}.json?offset={offset}"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"Fetched statements from {endpoint} with offset {offset}")
        return response.json().get('results', [])
    else:
        print(f"Error fetching statements from {endpoint}: Status code {response.status_code}")
        return []

def insert_congressional_statements(cursor, statements, stop_congress):
    for statement in statements:
        congress_number = statement.get('congress')
        if int(congress_number) >= stop_congress:
            insert_query = """
            INSERT INTO congressional_statements (url, date, title, statement_type, member_id, congress, chamber)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (statement_id) DO NOTHING;
            """
            params = (
                statement['url'],
                datetime.strptime(statement['date'], '%Y-%m-%d').date(),  
                statement['title'],
                statement.get('statement_type'), 
                statement['member_id'],
                statement.get('congress'),
                statement.get('chamber')
            )
            cursor.execute(insert_query, params)
            print(f"Inserted Congressional Statement from {statement['date']}")

def insert_committee_statements(cursor, statements):
    for statement in statements:
        insert_query = """
        INSERT INTO committee_statements (url, date, title, statement_type, committee_id, congress, chamber)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (statement_id) DO NOTHING;
        """

        params = (
            statement['url'],
            datetime.strptime(statement['date'], '%Y-%m-%d').date(),
            statement['title'],
            statement.get('statement_type'),
            statement['committee_id'],
            statement.get('congress'),
            statement.get('chamber')
        )
        cursor.execute(insert_query, params)
        print(f"Inserted Committee Statement from {statement['date']}")

# Main function
def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        # Process Congressional Statements
        offset = 0
        while True:
            statements = fetch_statements(api_key, 'latest', offset)
            if not statements:
                print(f"No more congressional statements to process at offset {offset}.")
                break
            insert_congressional_statements(cur, statements, 113)
            conn.commit()
            print(f"Processed {len(statements)} congressional statements at offset {offset}.")
            offset += 20

        # Process Committee Statements
        offset = 0
        while True:
            statements = fetch_statements(api_key, 'committees/latest', offset)
            if not statements:
                print(f"No more committee statements to process at offset {offset}.")
                break
            insert_committee_statements(cur, statements)
            conn.commit()
            print(f"Processed {len(statements)} committee statements at offset {offset}.")
            offset += 20

    except Exception as e:
        print(f"Error in main process: {e}")
        conn.rollback()
    finally:
        if cur:
            cur.close()
            print("Database cursor closed.")
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
