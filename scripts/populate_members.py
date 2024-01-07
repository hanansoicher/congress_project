import os
import psycopg2
import requests
from datetime import datetime

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

def fetch_all_members_from_congress(api_key, congress_number):
    # Fetch list of members from Congress
    base_url = "https://api.propublica.org/congress/v1/{}/{}/members.json"
    headers = {'X-API-Key': api_key}
    chambers = ['house', 'senate']
    all_members = []

    for chamber in chambers:
        url = base_url.format(congress_number, chamber)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            members = data.get('results')[0].get('members')
            all_members.extend(members)
            print(f"Successfully fetched {len(members)} members from {chamber} of congress {congress_number}")
        else:
            print(f"Error fetching data for {chamber} of congress {congress_number}: Status code {response.status_code}")
    return all_members

def fetch_member_details(api_key, member_id):
    # Fetch detailed information for a specific member
    url = f"https://api.propublica.org/congress/v1/members/{member_id}.json"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('results')[0]  # Detailed member data
    else:
        print(f"Error fetching data for member {member_id}: Status code {response.status_code}")
        return None

# Insert Member Data
def insert_member_data(cursor, member):
    insert_member_query = """
            INSERT INTO members (member_id, title, short_title, api_uri, first_name, middle_name, last_name, suffix, date_of_birth, gender, party, leadership_role, twitter_account, facebook_account, youtube_account, govtrack_id, cspan_id, votesmart_id, icpsr_id, crp_id, google_entity_id, fec_candidate_id, url, rss_url, contact_form, in_office, cook_pvi, dw_nominate, ideal_point, seniority, next_election, total_votes, missed_votes, total_present, last_updated, ocd_id, office, phone, fax, state, senate_class, state_rank, lis_id, missed_votes_pct, votes_with_party_pct, votes_against_party_pct) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """    
    member_params = (
        member.get('id', None),
        member.get('title', None),
        member.get('short_title', None),
        member.get('api_uri', None),
        member.get('first_name', None),
        member.get('middle_name', None),
        member.get('last_name', None),
        member.get('suffix', None),
        datetime.strptime(member['date_of_birth'], '%Y-%m-%d').date() if member.get('date_of_birth') else None,
        member.get('gender', None),
        member.get('party', None),
        member.get('leadership_role', None),
        member.get('twitter_account', None),
        member.get('facebook_account', None),
        member.get('youtube_account', None),
        member.get('govtrack_id', None),
        member.get('cspan_id', None),
        member.get('votesmart_id', None),
        member.get('icpsr_id', None),
        member.get('crp_id', None),
        member.get('google_entity_id', None),
        member.get('fec_candidate_id', None) if member.get('fec_candidate_id') != "" else None,
        member.get('url', None),
        member.get('rss_url', None),
        member.get('contact_form', None),
        member.get('in_office', None),
        member.get('cook_pvi', None),
        member.get('dw_nominate', None),
        member.get('ideal_point', None),
        member.get('seniority', None),
        member.get('next_election', None),
        member.get('total_votes', None),
        member.get('missed_votes', None),
        member.get('total_present', None),
        datetime.strptime(member['last_updated'], '%Y-%m-%d %H:%M:%S %z').isoformat() if member.get('last_updated') else None,
        member.get('ocd_id', None),
        member.get('office', None),
        member.get('phone', None),
        member.get('fax', None),
        member.get('state', None),
        member.get('senate_class', None),
        member.get('state_rank', None),
        member.get('lis_id', None),
        float(member['missed_votes_pct']) if member.get('missed_votes_pct') is not None else None,
        float(member['votes_with_party_pct']) if member.get('votes_with_party_pct') is not None else None,
        float(member['votes_against_party_pct']) if member.get('votes_against_party_pct') is not None else None
        )
    print(f"Inserting member data: {member}")
    try:
        cursor.execute(insert_member_query, member_params)
        print(f"Member data inserted for ID {member.get('id')}")
    except psycopg2.Error as e:
        print(f"Error inserting member data for ID {member.get('id')}: {e}")

def insert_member_role(cursor, member_id, role):
    insert_member_role_query = """
        INSERT INTO member_roles (member_id, congress, chamber, title, short_title, state, party, leadership_role, fec_candidate_id, seniority, district, at_large, ocd_id, start_date, end_date, office, phone, fax, contact_form, cook_pvi, dw_nominate, ideal_point, next_election, total_votes, missed_votes, total_present, senate_class, state_rank, lis_id, bills_sponsored, bills_cosponsored, missed_votes_pct, votes_with_party_pct, votes_against_party_pct) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    start_date = datetime.strptime(role['start_date'], '%Y-%m-%d').date() if role.get('start_date') else None
    end_date = datetime.strptime(role['end_date'], '%Y-%m-%d').date() if role.get('end_date') else None
    member_role_params = (
        member_id,
        role.get('congress', None),
        role.get('chamber', None),
        role.get('title', None),
        role.get('short_title', None),
        role.get('state', None),
        role.get('party', None),
        role.get('leadership_role', None),
        role.get('fec_candidate_id', None) if role.get('fec_candidate_id') != "" else None,
        role.get('seniority', None),
        role.get('district', None),
        role.get('at_large', None),
        role.get('ocd_id', None),
        start_date,
        end_date,
        role.get('office', None),
        role.get('phone', None),
        role.get('fax', None),
        role.get('contact_form', None),
        role.get('cook_pvi', None),
        role.get('dw_nominate', None),
        role.get('ideal_point', None),
        role.get('next_election', None),
        role.get('total_votes', None),
        role.get('missed_votes', None),
        role.get('total_present', None),
        role.get('senate_class', None),
        role.get('state_rank', None),
        role.get('lis_id', None),
        role.get('bills_sponsored', None),
        role.get('bills_cosponsored', None),
        float(role.get('missed_votes_pct', 0.0)) if role.get('missed_votes_pct') is not None else 0.0,
        float(role.get('votes_with_party_pct', 0.0)) if role.get('votes_with_party_pct') is not None else 0.0,
        float(role.get('votes_against_party_pct', 0.0)) if role.get('votes_against_party_pct') is not None else 0.0
    )
    try:
        cursor.execute(insert_member_role_query, member_role_params)
        print(f"Role data inserted for Member ID {member_id}, Congress {role.get('congress')}")
    except psycopg2.Error as e:
        print(f"Error inserting role data for Member ID {member_id}: {e}")



# Insert Committee and Subcommittee Data
def insert_committee_data(cursor, member_id, role):
    insert_member_committee_query = """
                        INSERT INTO member_committees (member_id, committee_name, committee_code, committee_api_uri, committee_side, committee_title, rank_in_party, committee_begin_date, committee_end_date) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
    insert_member_subcommittee_query = """
                        INSERT INTO member_subcommittees (subcommittee_name, subcommittee_code, subcommittee_parent_committee_id, subcommittee_api_uri, subcommittee_side, subcommittee_title, subcommittee_rank_in_party, subcommittee_begin_date, subcommittee_end_date) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
    for committee in role.get('committees', []):
        committee_params = (
                        member_id, 
                        committee.get('name', None),
                        committee.get('code', None),
                        committee.get('api_uri', None),
                        committee.get('side', None),
                        committee.get('title', None),
                        committee.get('rank_in_party', None),
                        datetime.strptime(committee['begin_date'], '%Y-%m-%d').date() if committee.get('begin_date') else None,
                        datetime.strptime(committee['end_date'], '%Y-%m-%d').date() if committee.get('end_date') else None,
        )
        try:
            cursor.execute(insert_member_committee_query, committee_params)
            print(f"Committee data inserted for Member ID {member_id}, Committee {committee.get('name')}")
        except psycopg2.Error as e:
            print(f"Error inserting committee data for Member ID {member_id}: {e}")

    for subcommittee in role.get('subcommittees', []):
        subcommittee_params = (
                    subcommittee.get('name', None),
                    subcommittee.get('code', None),
                    subcommittee.get('parent_committee_id', None),
                    subcommittee.get('api_uri', None),
                    subcommittee.get('side', None),
                    subcommittee.get('title', None),
                    subcommittee.get('rank_in_party', None),
                    datetime.strptime(subcommittee['begin_date'], '%Y-%m-%d').date() if subcommittee.get('begin_date') else None,
                    datetime.strptime(subcommittee['end_date'], '%Y-%m-%d').date() if subcommittee.get('end_date') else None,
                )
        try:
            cursor.execute(insert_member_subcommittee_query, subcommittee_params)
            print(f"Subcommittee data inserted for Member ID {member_id}, Subcommittee {subcommittee.get('name')}")
        except psycopg2.Error as e:
            print(f"Error inserting subcommittee data for Member ID {member_id}: {e}")


# Execute Query Helper
def execute_query(cursor, query, params):
    try:
        cursor.execute(query, params)
        print("Query executed successfully.")
    except psycopg2.Error as e:
        print(f"Error executing query: {e}\nQuery: {query}\nParams: {params}")


def insert_members(cursor, members, api_key):
    for member_summary in members:
        member_id = member_summary.get('id')
        member_details = fetch_member_details(api_key, member_id)
        if member_details:
            insert_member_data(cursor, member_details)
            for role in member_details.get('roles', []):
                insert_member_role(cursor, member_id, role)
                insert_committee_data(cursor, member_id, role)


def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    conn = connect_to_db()
    while conn:
        print("Successfully connected to the database.")
        cur = conn.cursor()
        for congress_number in range(113, 119):
            print(f"Fetching and inserting data for congress number {congress_number}...")
            members_data = fetch_all_members_from_congress(api_key, congress_number)
            insert_members(cur, members_data, api_key)
            print(f"Completed data insertion for congress number {congress_number}.")
            conn.commit()
        cur.close()
        conn.close()
        print("Database update completed successfully.")
    print("Failed to connect to the database.")

if __name__ == "__main__":
    main()