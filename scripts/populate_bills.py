from collections import defaultdict
import json
import os
import psycopg2
from datetime import datetime
import requests

# JSON Decode Error: Invalid \escape: line 671 column 1793 (char 82010)

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


def fetch_bills(api_key, congress_number, chamber, bill_type, offset=0):
    url = f"https://api.propublica.org/congress/v1/{congress_number}/{chamber}/bills/{bill_type}.json?offset={offset}"
    headers = {'X-API-Key': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print("Raw response:", "response.text")
            return None  # Or handle the error as needed
    else:
        print(f"Error fetching data: Status code {response.status_code}")
        return None
    
# Fetch all bills from Congress
def fetch_all_bills_from_congress(api_key, congress_number, bill_type):
    chambers = ['house', 'senate']
    all_bills = []

    for chamber in chambers:
        offset = 0
        while True:
            data = fetch_bills(api_key, congress_number, chamber, bill_type, offset)
            if data and data.get('results'):
                bills = data.get('results')[0].get('bills')
                all_bills.extend(bills)
                print(f"Fetched {len(bills)} {bill_type} bills from {chamber} of congress {congress_number}, offset {offset}")
                if len(bills) == 0:
                    break
                offset += len(bills)
            else:
                break
    return all_bills

# Insert bills into database
def insert_bills(cursor, bills):
    for bill in bills:
        # Insert into bills table
        insert_bill_query = """
            INSERT INTO bills (bill_id, congress, chamber, bill_type, number, bill_uri, title, short_title, sponsor_title, sponsor_id, sponsor_name, sponsor_state, sponsor_party, sponsor_uri, gpo_pdf_uri, congressdotgov_url, govtrack_url, introduced_date, active, last_vote, house_passage, senate_passage, enacted, vetoed, cosponsors, primary_subject, summary, summary_short, latest_major_action_date, latest_major_action) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (bill_id) DO NOTHING;
        """
        bill_params = (
            bill.get('bill_id'), bill.get('congress'), bill.get('chamber'), bill.get('bill_type'), bill.get('number'), bill.get('bill_uri'), bill.get('title'),
            bill.get('short_title'), bill.get('sponsor_title'), bill.get('sponsor_id'), bill.get('sponsor_name'), bill.get('sponsor_state'), bill.get('sponsor_party'), 
            bill.get('sponsor_uri'), bill.get('gpo_pdf_uri'), bill.get('congressdotgov_url'), bill.get('govtrack_url'), bill.get('introduced_date'), 
            bill.get('active'), bill.get('last_vote'), bill.get('house_passage'), bill.get('senate_passage'), bill.get('enacted'), bill.get('vetoed'), 
            bill.get('cosponsors'), bill.get('primary_subject'), bill.get('summary'), bill.get('summary_short'), bill.get('latest_major_action_date'), bill.get('latest_major_action')
        )

        # Execute query
        try:
            cursor.execute(insert_bill_query, bill_params)
            print(f"Bill data inserted for {bill['bill_id']}")
        except psycopg2.Error as e:
            print(f"Error inserting bill data for {bill['bill_id']}: {e}")

        # Insert into cosponsors_by_party table
        for party, count in bill.get('cosponsors_by_party', {}).items():
            insert_cosponsors_query = """
                INSERT INTO cosponsors_by_party (bill_id, party, count)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """
            cosponsor_params = (bill['bill_id'], party, count)
            try:
                cursor.execute(insert_cosponsors_query, cosponsor_params)
                print(f"Cosponsor data inserted for {bill['bill_id']} and party {party}")
            except psycopg2.Error as e:
                print(f"Error inserting cosponsor data for {bill['bill_id']} and party {party}: {e}")

        # Insert into bill_committees table
        for committee_code in bill.get('committee_codes', []):
            insert_committee_query = """
                INSERT INTO bill_committees (bill_id, committee_code)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """
            committee_params = (bill['bill_id'], committee_code)
            try:
                cursor.execute(insert_committee_query, committee_params)
                print(f"Committee data inserted for {bill['bill_id']} and committee code {committee_code}")
            except psycopg2.Error as e:
                print(f"Error inserting committee data for {bill['bill_id']} and committee code {committee_code}: {e}")

        # Insert into bill_subcommittees table
        for subcommittee_code in bill.get('subcommittee_codes', []):
            insert_subcommittee_query = """
                INSERT INTO bill_subcommittees (bill_id, subcommittee_code)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """
            subcommittee_params = (bill['bill_id'], subcommittee_code)
            try:
                cursor.execute(insert_subcommittee_query, subcommittee_params)
                print(f"Subcommittee data inserted for {bill['bill_id']} and subcommittee code {subcommittee_code}")
            except psycopg2.Error as e:
                print(f"Error inserting subcommittee data for {bill['bill_id']} and subcommittee code {subcommittee_code}: {e}")

def main():
    api_key = 'sZSfHfYSsUR5gN3OzCYoxhwUZq2WMEbATy4L2m0U'
    conn = connect_to_db()
    if conn:
        print("Successfully connected to the database.")
        cur = conn.cursor()
        bill_types = ['introduced']
        for congress_number in range(117, 119):
            for bill_type in bill_types:
                bills_data = fetch_all_bills_from_congress(api_key, congress_number, bill_type)
                insert_bills(cur, bills_data)
                conn.commit()
        cur.close()
        conn.close()
        print("Database update completed successfully.")
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    main()