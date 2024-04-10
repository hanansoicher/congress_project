import sqlite3
from transformers import pipeline

def summarize_reports_for_subindustry(subindustry_id):
    conn_reports = sqlite3.connect('./data/reports_db.sqlite')
    cursor_reports = conn_reports.cursor()

    cursor_reports.execute("SELECT report_text FROM report_classifications WHERE ClassifiedSubIndustries LIKE ? ORDER BY similarity_score DESC LIMIT 5", (f'%{subindustry_id}%',))
    top_reports = [row[0] for row in cursor_reports.fetchall()]

    conn_reports.close()

    conn_industries = sqlite3.connect('./data/industry_db.sqlite')
    cursor_industries = conn_industries.cursor()

    cursor_industries.execute("SELECT description FROM industries WHERE SubIndustryId = ?", (subindustry_id,))
    subindustry_description = cursor_industries.fetchone()[0]

    combined_text = subindustry_description + ' ' + ' '.join(top_reports)

    summarizer = pipeline("summarization")

    summary = summarizer(combined_text, max_length=512, min_length=100, do_sample=False)[0]['summary_text']

    cursor_industries.execute("UPDATE industries SET summarized_description = ? WHERE SubIndustryId = ?", (summary, subindustry_id))
    conn_industries.commit()

    conn_industries.close()

def update_all_subindustries():
    conn_industries = sqlite3.connect('./data/industry_db.sqlite')
    cursor_industries = conn_industries.cursor()

    cursor_industries.execute("SELECT SubIndustryId FROM industries")
    subindustry_ids = [row[0] for row in cursor_industries.fetchall()]

    conn_industries.close()

    for subindustry_id in subindustry_ids:
        summarize_reports_for_subindustry(subindustry_id)
        print(f"Updated summarized description for subindustry {subindustry_id}")

if __name__ == "__main__":
    update_all_subindustries()
