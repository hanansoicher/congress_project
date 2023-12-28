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

# Fetch Committee Data
def fetch_committees(api_key, congress, chamber):
    url = f"https://api.propublica.org/congress/v1/{congress}/{chamber}/committees.json"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        results = json_response.get('results', [])
        if results:  # Check if 'results' is not an empty list
            return results[0].get('committees', [])
        else:
            print(f"No results found for congress {congress} and chamber {chamber}")
            return []
    else:
        print(f"Error fetching committees data: Status code {response.status_code}")
        return []


# Fetch Detailed Committee Data
def fetch_committee_details(api_key, congress, chamber, committee_id):
    url = f"https://api.propublica.org/congress/v1/{congress}/{chamber}/committees/{committee_id}.json"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('results', [])[0]
    else:
        print(f"Error fetching committee details for {committee_id}: Status code {response.status_code}")
        return None

# Function to insert committees data
def insert_committee_data(cursor, committee_details, chamber):
    # Insert committee data
    committee_query = """
        INSERT INTO committees (committee_id, name, chamber, url, api_uri, chair_id, ranking_member_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (committee_id) DO NOTHING;
    """
    committee_params = (
        committee_details['id'],
        committee_details['name'],
        chamber,
        committee_details.get('url'),
        committee_details.get('api_uri'),
        committee_details.get('chair_id'),
        committee_details.get('ranking_member_id')
    )
    cursor.execute(committee_query, committee_params)

    # Insert subcommittee data
    for subcommittee in committee_details.get('subcommittees', []):
        subcommittee_query = """
            INSERT INTO subcommittees (subcommittee_id, committee_id, name, api_uri)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (subcommittee_id) DO NOTHING;
        """
        subcommittee_params = (
            subcommittee['id'],
            committee_details['id'],
            subcommittee['name'],
            subcommittee.get('api_uri')
        )
        cursor.execute(subcommittee_query, subcommittee_params)

    # Insert committee members data
    for member in committee_details.get('current_members', []):
        committee_member_query = """
            INSERT INTO committee_members (member_id, committee_id, role)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        committee_member_params = (
            member['id'],
            committee_details['id'],
            member.get('role', 'member')  # default role to 'member' if not specified
        )
        cursor.execute(committee_member_query, committee_member_params)


# Function to insert subcommittees data
def insert_subcommittees(cursor, subcommittees, committee_id):
    for subcommittee in subcommittees:
        insert_query = """
            INSERT INTO subcommittees (subcommittee_id, committee_id, name, api_uri) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (subcommittee_id) DO NOTHING;
        """
        params = (subcommittee['id'], committee_id, subcommittee['name'], subcommittee.get('api_uri'))
        cursor.execute(insert_query, params)

# Main function
def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        for congress_number in range(117, 119):  # Adjust the range as needed
            for chamber in ['house', 'senate', 'joint']:
                try:
                    committees = fetch_committees(api_key, congress_number, chamber)
                    for committee in committees:
                        committee_details = fetch_committee_details(api_key, congress_number, chamber, committee['id'])
                        if committee_details:
                            insert_committee_data(cur, committee_details, chamber)  # Pass the correct chamber
                    conn.commit()
                except Exception as e:
                    print(f"Error processing {congress_number} {chamber}: {e}")
                    conn.rollback()
        cur.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    main()
