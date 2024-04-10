import sqlite3
import requests
import time
import json

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'
RATE_LIMIT_CODE = 429
RATE_LIMIT_WAIT = 1800

def fetch_report_info_from_db(rowid):
    conn = sqlite3.connect('politics_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT ReportNumber FROM committee_reports WHERE rowid = ?", (rowid,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def parse_report_number(report_number):
    parts = report_number.split()
    report_type = parts[0] + parts[1].replace('ept.', 'pt.')
    report_type = report_type.replace('.', '').lower()
    congress, number = parts[2].split('-')
    return report_type, congress, number


def fetch_report_text(report_type, congress, number):
    print(report_type, number, congress)
    text_url = f"{BASE_URL}/committee-report/{congress}/{report_type}/{number}/text?api_key={API_KEY}"
    attempt = 0
    while attempt < 3:
        response = requests.get(text_url)
        if response.status_code == RATE_LIMIT_CODE:
            print("Rate limit exceeded. Waiting to retry...")
            time.sleep(RATE_LIMIT_WAIT)
            attempt += 1
            continue
        elif response.status_code == 200:
            try:
                data = json.loads(response.text)
                for item in data.get('text', []):
                    for format_item in item.get('formats', []):
                        if format_item.get('type') == 'Formatted Text':
                            return requests.get(format_item.get('url')).text
                print("Formatted Text URL not found in JSON.")
                return ""
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return ""
        else:
            print(f"Failed to fetch report text: HTTP {response.status_code}")
            return ""
        break

def update_report_text_in_db(rowid, report_text):
    conn = sqlite3.connect('politics_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("UPDATE committee_reports SET report_text = ? WHERE rowid = ?", (report_text, rowid))
    conn.commit()
    conn.close()

def main():
    conn = sqlite3.connect('politics_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT rowid FROM committee_reports")
    rowids = cursor.fetchall()
    conn.close()

    for rowid in rowids:
        rowid = rowid[0]
        report_number = fetch_report_info_from_db(rowid)
        if report_number:
            report_type, congress, number = parse_report_number(report_number)
            print(f"Fetching report text for {report_number}...")
            report_text = fetch_report_text(report_type, congress, number)
            if report_text:
                update_report_text_in_db(rowid, report_text)
            else:
                print(f"Failed to fetch report text for {report_number}")
        else:
            print(f"No report info found in database for rowid {rowid}")

    print("Report text fetching and updating completed.")

if __name__ == "__main__":
    main()
