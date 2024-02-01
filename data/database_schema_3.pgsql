DROP TABLE IF EXISTS member_roles;
DROP TABLE IF EXISTS committee_members;
DROP TABLE IF EXISTS member_committees;
DROP TABLE IF EXISTS member_subcommittees;
DROP TABLE IF EXISTS cosponsors_by_party;
DROP TABLE IF EXISTS bill_committees;
DROP TABLE IF EXISTS bill_subcommittees;
DROP TABLE IF EXISTS subcommittees;
DROP TABLE IF EXISTS member_votes;
DROP TABLE IF EXISTS congressional_statements;
DROP TABLE IF EXISTS committee_statements;
DROP TABLE IF EXISTS committees;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS bills;

CREATE TABLE IF NOT EXISTS members (
    member_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    last_name VARCHAR(50),
    suffix VARCHAR(10),
    date_of_birth DATE,
    gender CHAR(1),
    url VARCHAR(255),
    govtrack_id VARCHAR(50),
    cspan_id VARCHAR(50),
    votesmart_id VARCHAR(50),
    icpsr_id VARCHAR(50),
    twitter_account VARCHAR(50),
    facebook_account VARCHAR(50),
    youtube_account VARCHAR(50),
    crp_id VARCHAR(50),
    google_entity_id VARCHAR(50),
    rss_url VARCHAR(255),
    in_office BOOLEAN,
    current_party CHAR(2),
    most_recent_vote DATE,
    last_updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS member_roles (
    id SERIAL PRIMARY KEY,
    member_id VARCHAR(20),
    congress INT,
    chamber VARCHAR(10),
    title VARCHAR(255),
    short_title VARCHAR(50),
    state CHAR(2),
    party CHAR(2),
    leadership_role VARCHAR(255),
    fec_candidate_id VARCHAR(255),
    seniority INT,
    district VARCHAR(50),
    at_large BOOLEAN,
    ocd_id VARCHAR(255),
    start_date DATE,
    end_date DATE,
    office VARCHAR(255),
    phone VARCHAR(20),
    fax VARCHAR(20),
    contact_form VARCHAR(255),
    cook_pvi VARCHAR(10),
    dw_nominate REAL,
    ideal_point REAL,
    next_election VARCHAR(10),
    total_votes INT,
    missed_votes INT,
    total_present INT,
    senate_class VARCHAR(50),
    state_rank VARCHAR(50),
    lis_id VARCHAR(50),
    bills_sponsored INT,
    bills_cosponsored INT,
    missed_votes_pct REAL,
    votes_with_party_pct REAL,
    votes_against_party_pct REAL
);

CREATE TABLE IF NOT EXISTS committees (
    committee_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    chamber VARCHAR(10),
    url VARCHAR(255),
    api_uri VARCHAR(255),
    chair_id VARCHAR(20),
    ranking_member_id VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS subcommittees (
    subcommittee_id VARCHAR(10) PRIMARY KEY,
    parent_committee_id VARCHAR(10),
    name VARCHAR(255),
    code VARCHAR(10),
    api_uri VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS committee_members (
    id SERIAL PRIMARY KEY,
    member_id VARCHAR(20),
    committee_id VARCHAR(10),
    subcommittee_id VARCHAR(10),
    role VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS member_committees (
    id SERIAL PRIMARY KEY,
    member_id VARCHAR(20),
    committee_id VARCHAR(10),
    role VARCHAR(50),
    rank_in_party INT,
    begin_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS member_subcommittees (
    id SERIAL PRIMARY KEY,
    member_id VARCHAR(20),
    subcommittee_id VARCHAR(10),
    role VARCHAR(50),
    rank_in_party INT,
    begin_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS bills (
    bill_id VARCHAR(20) PRIMARY KEY,
    congress INT,
    chamber VARCHAR(10),
    bill_type VARCHAR(10),
    number VARCHAR(20),
    bill_uri VARCHAR(255),
    title TEXT,
    short_title TEXT,
    sponsor_title VARCHAR(50),
    sponsor_id VARCHAR(20),
    sponsor_name VARCHAR(100),
    sponsor_state CHAR(2),
    sponsor_party CHAR(2),
    sponsor_uri VARCHAR(255),
    gpo_pdf_uri VARCHAR(255),
    congressdotgov_url VARCHAR(255),
    govtrack_url VARCHAR(255),
    introduced_date DATE,
    active BOOLEAN,
    last_vote DATE,
    house_passage DATE,
    senate_passage DATE,
    enacted DATE,
    vetoed DATE,
    cosponsors INT,
    primary_subject VARCHAR(100),
    summary TEXT,
    summary_short TEXT,
    latest_major_action_date DATE,
    latest_major_action TEXT
);

CREATE TABLE IF NOT EXISTS cosponsors_by_party (
    bill_id VARCHAR(20),
    party CHAR(2),
    count INT
);

CREATE TABLE IF NOT EXISTS bill_committees (
    bill_id VARCHAR(20),
    committee_code VARCHAR(10),
    committee_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS bill_subcommittees (
    bill_id VARCHAR(20),
    subcommittee_code VARCHAR(10),
    subcommittee_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS votes (
    vote_id SERIAL PRIMARY KEY,
    congress INTEGER,
    session INTEGER,
    chamber VARCHAR(10),
    roll_call INTEGER,
    bill_id VARCHAR(20),
    question TEXT,
    description TEXT,
    vote_type VARCHAR(20),
    date DATE,
    result VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS member_votes (
    member_vote_id SERIAL PRIMARY KEY,
    vote_id INTEGER,
    member_id VARCHAR(20),
    vote_position VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS congressional_statements (
    statement_id SERIAL PRIMARY KEY,
    url VARCHAR(255),
    date DATE,
    title TEXT,
    statement_type VARCHAR(50),
    member_id VARCHAR(20),
    congress INTEGER,
    chamber VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS committee_statements (
    statement_id SERIAL PRIMARY KEY,
    url VARCHAR(255),
    date DATE,
    title TEXT,
    statement_type VARCHAR(50),
    committee_id VARCHAR(10),
    congress INTEGER,
    chamber VARCHAR(10)
);

CREATE INDEX idx_votes_congress ON votes(congress);
CREATE INDEX idx_votes_chamber ON votes(chamber);
CREATE INDEX idx_votes_bill_id ON votes(bill_id);
CREATE INDEX idx_member_votes_member_id ON member_votes(member_id);
CREATE INDEX idx_member_votes_vote_id ON member_votes(vote_id);

-- Indexes for faster queries
CREATE INDEX idx_bill_congress ON bills(congress);
CREATE INDEX idx_bill_chamber ON bills(chamber);
CREATE INDEX idx_bill_sponsor_id ON bills(sponsor_id);
