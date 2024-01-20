import os
import psycopg2
import requests

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

def fetch_committees(api_key, congress, chamber):
    url = f"https://api.propublica.org/congress/v1/{congress}/{chamber}/committees.json"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        results = json_response.get('results', [])
        if results:
            committees = results[0].get('committees', [])
            print(f"Fetched {len(committees)} committees for Congress {congress}, Chamber {chamber}.")
            return committees
        else:
            print(f"No results found for Congress {congress} and Chamber {chamber}.")
            return []
    else:
        print(f"Error fetching committees data: Status code {response.status_code}")
        return []

def fetch_committee_details(api_key, congress, chamber, committee_id):
    url = f"https://api.propublica.org/congress/v1/{congress}/{chamber}/committees/{committee_id}.json"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        committee_details = response.json().get('results', [])[0]
        print(f"Fetched details for Committee ID {committee_id} in Congress {congress}, Chamber {chamber}.")
        return committee_details
    else:
        print(f"Error fetching committee details for {committee_id}: Status code {response.status_code}")
        return None

def insert_committee_members(cursor, committee_details):
    for member in committee_details.get('current_members', []):
        committee_member_query = """
            INSERT INTO committee_members (member_id, committee_id, role)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        committee_member_params = (
            member['id'],
            committee_details['id'],
            member.get('role', 'member')
        )
        try:
            cursor.execute(committee_member_query, committee_member_params)
            print(f"Inserted committee member {member['name']} (ID: {member['id']}) into committee {committee_details['name']} (ID: {committee_details['id']}).")
        except psycopg2.Error as e:
            print(f"Error inserting member {member['id']} into committee {committee_details['id']}: {e}")

def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        for congress_number in range(113, 119):
            for chamber in ['house', 'senate', 'joint']:
                committees = fetch_committees(api_key, congress_number, chamber)
                for committee in committees:
                    committee_details = fetch_committee_details(api_key, congress_number, chamber, committee['id'])
                    if committee_details:
                        insert_committee_members(cur, committee_details)
                conn.commit()
                print(f"Committee member data committed for Congress {congress_number}, Chamber {chamber}.")
        cur.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
