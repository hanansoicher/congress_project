import time
import pandas as pd
import requests
import psycopg2
import psycopg2.extras

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'

def fetch_committee_report(congress, report_type, report_number):
    url = f"{BASE_URL}/committee-report/{congress}/{report_type}/{report_number}?api_key={API_KEY}"
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Successfully fetched report: {congress}, {report_type}, {report_number}")
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Waiting for 1 hour...")
            time.sleep(3600)  # Wait for 1 hour
        else:
            print(f"Error fetching report: HTTP {response.status_code}")
            return None

def insert_into_database(report_data):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname='politics_db',
            user='postgres',
            password='Ignorantbliss(9)',
            host='localhost'
        )
        cursor = conn.cursor()

        # Insert into committee_reports
        print(f"Inserting report data: {report_data}")
        cursor.execute("""
            INSERT INTO committee_reports (
                congress, chamber, is_conference_report, issue_date, 
                report_number, part, session_number, text_url, title, 
                report_type, update_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING report_id;
        """, (
            report_data['congress'],
            report_data['chamber'],
            report_data['isConferenceReport'],
            report_data['issueDate'],
            report_data['number'],
            report_data['part'],
            report_data['sessionNumber'],
            report_data['text']['url'],
            report_data['title'],
            report_data['type'],
            report_data['updateDate']
        ))

        report_id_result = cursor.fetchone()
        if report_id_result is not None:
            report_id = report_id_result[0]
            print(f"Inserted report with ID: {report_id}")

            for bill in report_data['associatedBill']:
                print(f"Inserting associated bill: {bill}")
                cursor.execute("""
                    INSERT INTO associated_bills (
                        report_id, congress, bill_number, bill_type, bill_url
                    ) VALUES (%s, %s, %s, %s, %s);
                """, (
                    report_id,
                    bill['congress'],
                    bill['number'],
                    bill['type'],
                    bill['url']
                ))
        else:
            print("No report ID returned from INSERT operation.")

        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if conn is not None:
            conn.close()

def main():
    reports_df = pd.read_csv('./data/committee_reports_115-118.csv')
    print("Starting report processing...")
    for index, row in reports_df.iterrows():
        report_number_parts = row['Report Number'].split()[-1].split('-')
        report_type_code = 'hrpt' if row['Report Number'].startswith('H') else 'srpt' if row['Report Number'].startswith('S') else 'erpt' if row['Report Number'].startswith('E') else 'hrpt'
        report_data = fetch_committee_report(report_number_parts[0], report_type_code, report_number_parts[-1])
        if report_data and 'committeeReports' in report_data:
            for report in report_data['committeeReports']:
                insert_into_database(report)

if __name__ == '__main__':
    main()