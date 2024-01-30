CREATE TABLE committee_reports (
    id SERIAL PRIMARY KEY,
    congress INTEGER,
    chamber VARCHAR(255),
    is_conference_report BOOLEAN,
    issue_date TIMESTAMP,
    report_number INTEGER,
    part INTEGER,
    session_number INTEGER,
    text_url VARCHAR(255),
    title TEXT,
    report_type VARCHAR(255),
    update_date TIMESTAMP
);

CREATE TABLE associated_bills (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES committee_reports(id),
    congress INTEGER,
    bill_number VARCHAR(255),
    bill_type VARCHAR(255),
    bill_url VARCHAR(255)
);
