import requests
import psycopg2

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

def fetch_committee_and_subcommittee_details(api_key):
    committee_details = []
    subcommittee_details = []
    for congress_number in range(113, 119):
        for chamber in ['house', 'senate', 'joint']:
            url = f"https://api.propublica.org/congress/v1/{congress_number}/{chamber}/committees.json"
            headers = {'X-API-Key': api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_response = response.json()
                results = json_response.get('results', [])
                if results:
                    for committee in results[0].get('committees', []):
                        committee_detail = (
                            committee['id'],
                            committee['name'],
                            chamber,
                            committee.get('url', ''),
                            committee.get('api_uri', ''),
                            committee.get('chair_id', ''),
                            committee.get('ranking_member_id', '')
                        )
                        committee_details.append(committee_detail)

                        for subcommittee in committee.get('subcommittees', []):
                            subcommittee_detail = (
                                subcommittee['id'],
                                committee['id'],
                                subcommittee['name'],
                                subcommittee.get('api_uri', ''),
                            )
                            subcommittee_details.append(subcommittee_detail)
                else:
                    print(f"No results found for congress {congress_number} and chamber {chamber}")
            else:
                print(f"Error fetching committees data: Status code {response.status_code}")
    return committee_details, subcommittee_details

def insert_committee_details_to_db(committee_details, conn):
    cur = conn.cursor()
    for detail in committee_details:
        try:
            cur.execute("INSERT INTO committees (committee_id, name, chamber, url, api_uri, chair_id, ranking_member_id) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (committee_id) DO NOTHING;", detail)
        except psycopg2.Error as e:
            print(f"Error inserting committee details {detail[0]}: {e}")
    conn.commit()

def insert_subcommittee_details_to_db(subcommittee_details, conn):
    cur = conn.cursor()
    for detail in subcommittee_details:
        try:
            cur.execute("INSERT INTO subcommittees (subcommittee_id, parent_committee_id, name, api_uri) VALUES (%s, %s, %s, %s) ON CONFLICT (subcommittee_id) DO NOTHING;", detail)
        except psycopg2.Error as e:
            print(f"Error inserting subcommittee details {detail[0]}: {e}")
    conn.commit()
    cur.close()

def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    committee_details, subcommittee_details = fetch_committee_and_subcommittee_details(api_key)
    conn = connect_to_db()
    if conn is not None:
        insert_committee_details_to_db(committee_details, conn)
        insert_subcommittee_details_to_db(subcommittee_details, conn)
        conn.close()

if __name__ == "__main__":
    main()
