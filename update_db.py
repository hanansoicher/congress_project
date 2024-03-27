import sqlite3
import requests
import json

API_KEY = 'Gej1jav3dg99KkJbAqneBc40kxt7pbeyODF9r1Tt'
BASE_URL = 'https://api.congress.gov/v3'

def parse_report_number(report_number):
    parts = report_number.split()
    report_type = parts[0] + parts[1].replace('ept.', 'pt.')
    report_type = report_type.replace('.', '').lower()
    congress, number = parts[2].split('-')
    return report_type, congress, number

def fetch_report_text(report_type, congress, number):
    text_url = f"{BASE_URL}/committee-report/{congress}/{report_type}/{number}/text?api_key={API_KEY}"
    response = requests.get(text_url)
    if response.status_code == 200:
        data = json.loads(response.text)
        for item in data.get('text', []):
            for format_item in item.get('formats', []):
                if format_item.get('type') == 'Formatted Text':
                    return requests.get(format_item.get('url')).text
        return ""
    else:
        return ""

def main():
    conn = sqlite3.connect('politics_db.sqlite')
    cursor = conn.cursor()

    # Find rows with empty report_text
    cursor.execute("SELECT rowid, ReportNumber FROM committee_reports WHERE report_text IS NULL OR report_text = ''")
    rows = cursor.fetchall()

    for rowid, report_number in rows:
        report_type, congress, number = parse_report_number(report_number)
        report_text = fetch_report_text(report_type, congress, number)
        if report_text:
            cursor.execute("UPDATE committee_reports SET report_text = ? WHERE rowid = ?", (report_text, rowid))
            conn.commit()
            print(f"Updated report text for rowid {rowid}")
        else:
            print(f"Failed to fetch report text for rowid {rowid}")

    conn.close()

if __name__ == "__main__":
    main()
