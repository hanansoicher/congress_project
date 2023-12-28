import requests
import psycopg2
import os
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
    try:
        return psycopg2.connect(**db_conn_info)
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        return None

# Function to fetch recent votes
def fetch_recent_votes(api_key, chamber, offset=0):
    url = f"https://api.propublica.org/congress/v1/{chamber}/votes/recent.json?offset={offset}"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# Function to fetch individual vote details
def fetch_vote_details(api_key, congress, chamber, session, roll_call):
    url = f"https://api.propublica.org/congress/v1/{congress}/{chamber}/sessions/{session}/votes/{roll_call}.json"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# Function to check if bill exists in the database
def bill_exists(cursor, bill_id):
    cursor.execute("SELECT 1 FROM bills WHERE bill_id = %s;", (bill_id,))
    return cursor.fetchone() is not None

# Function to process and store votes data
def process_and_store_votes(cursor, votes_data, api_key):
    if 'results' in votes_data and 'votes' in votes_data['results']:
        for i, vote_summary in enumerate(votes_data['results']['votes']):
            detailed_vote = fetch_vote_details(api_key, vote_summary['congress'], vote_summary['chamber'], vote_summary['session'], vote_summary['roll_call'])
            if detailed_vote and 'results' in detailed_vote and 'votes' in detailed_vote['results'] and 'vote' in detailed_vote['results']['votes']:
                vote = detailed_vote['results']['votes']['vote']
                bill_id = vote.get('bill', {}).get('bill_id')

                if bill_id and not bill_exists(cursor, bill_id):
                    print(f"Skipped: Vote {i+1} for non-existent bill {bill_id}")
                    continue

                cursor.execute("""
                    INSERT INTO votes (congress, session, chamber, roll_call, bill_id, question, description, vote_type, date, result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING vote_id;
                """, (
                    vote['congress'],
                    vote['session'],
                    vote['chamber'],
                    vote['roll_call'],
                    bill_id,  # Can be None
                    vote['question'],
                    vote['description'],
                    vote['vote_type'],
                    datetime.strptime(vote['date'], '%Y-%m-%d').date(),
                    vote['result']
                ))
                vote_id = cursor.fetchone()[0]
                print(f"Processed: Vote {i+1} inserted with ID {vote_id}")

                for position in vote['positions']:
                    cursor.execute("""
                        INSERT INTO member_votes (vote_id, member_id, vote_position)
                        VALUES (%s, %s, %s);
                    """, (
                        vote_id,
                        position['member_id'],
                        position['vote_position']
                    ))
            else:
                print(f"Warning: Vote details not found or in unexpected format for summary {i+1}")
    else:
        print("Error: Votes data not found or in unexpected format")

def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    chambers = ['house', 'senate', 'joint']
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        for chamber in chambers:
            offset = 0
            while True:
                recent_votes_data = fetch_recent_votes(api_key, chamber, offset)
                if recent_votes_data and 'results' in recent_votes_data and 'votes' in recent_votes_data['results']:
                    num_results = len(recent_votes_data['results']['votes'])
                    if num_results == 0 | offset == 4000:
                        break

                    process_and_store_votes(cur, recent_votes_data, api_key)
                    conn.commit()
                    print(f"Info: {num_results} votes processed for {chamber} (Offset: {offset}).")
                    offset += num_results
                else:
                    print(f"Error: Failed to fetch or no more votes data for {chamber} (Offset: {offset}).")
                    break
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()