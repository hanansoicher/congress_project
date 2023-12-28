-- Members Table
CREATE TABLE members (
    member_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(50),
    short_title VARCHAR(20),
    api_uri VARCHAR(255),
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50) NULL,
    last_name VARCHAR(50) NOT NULL,
    suffix VARCHAR(10) NULL,
    date_of_birth DATE NULL,
    gender CHAR(1),
    party CHAR(2),
    leadership_role VARCHAR(100) NULL,
    twitter_account VARCHAR(50) NULL,
    facebook_account VARCHAR(50) NULL,
    youtube_account VARCHAR(50) NULL,
    govtrack_id VARCHAR(50) NULL,
    cspan_id VARCHAR(50) NULL,
    votesmart_id VARCHAR(50) NULL,
    icpsr_id VARCHAR(50) NULL,
    crp_id VARCHAR(50) NULL,
    google_entity_id VARCHAR(50) NULL,
    fec_candidate_id VARCHAR(50) NULL,
    url VARCHAR(255) NULL,
    rss_url VARCHAR(255) NULL,
    contact_form VARCHAR(255) NULL,
    in_office BOOLEAN,
    cook_pvi VARCHAR(10) NULL,
    dw_nominate REAL NULL,
    ideal_point VARCHAR(50) NULL,
    seniority INT,
    next_election VARCHAR(10),
    total_votes INT,
    missed_votes INT,
    total_present INT,
    last_updated TIMESTAMP NULL,
    ocd_id VARCHAR(50) NULL,
    office VARCHAR(100) NULL,
    phone VARCHAR(20) NULL,
    fax VARCHAR(20) NULL,
    state CHAR(2),
    senate_class VARCHAR(10) NULL,
    state_rank VARCHAR(50) NULL,
    lis_id VARCHAR(10) NULL,
    missed_votes_pct REAL NULL,
    votes_with_party_pct REAL NULL,
    votes_against_party_pct REAL NULL
);

-- Member Roles Table
CREATE TABLE member_roles (
    member_id VARCHAR(255),
    congress VARCHAR(3),
    chamber VARCHAR(10),
    title VARCHAR(255),
    short_title VARCHAR(255),
    state VARCHAR(2),
    party VARCHAR(10),
    leadership_role VARCHAR(255) NULL,
    fec_candidate_id VARCHAR(255) NULL,
    seniority INTEGER,
    district VARCHAR(255) NULL,
    at_large BOOLEAN,
    ocd_id VARCHAR(255) NULL,
    start_date DATE NULL,
    end_date DATE NULL,
    office VARCHAR(255) NULL,
    phone VARCHAR(20) NULL,
    fax VARCHAR(20) NULL,
    contact_form VARCHAR(255) NULL,
    cook_pvi VARCHAR(10) NULL,
    dw_nominate FLOAT NULL,
    ideal_point FLOAT NULL,
    next_election VARCHAR,
    total_votes INTEGER,
    missed_votes INTEGER,
    total_present INTEGER,
    senate_class VARCHAR(255) NULL,
    state_rank VARCHAR(255) NULL,
    lis_id VARCHAR(255) NULL,
    bills_sponsored INTEGER NULL,
    bills_cosponsored INTEGER NULL,
    missed_votes_pct FLOAT NULL,
    votes_with_party_pct FLOAT NULL,
    votes_against_party_pct FLOAT NULL,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE committees (
    committee_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    chamber VARCHAR(10) NOT NULL,
    url VARCHAR(255) NULL,
    api_uri VARCHAR(255) NULL,
    chair_id VARCHAR(20),
    ranking_member_id VARCHAR(20)
);

CREATE TABLE subcommittees (
    subcommittee_id VARCHAR(10) PRIMARY KEY,
    committee_id VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    api_uri VARCHAR(255) NULL,
    FOREIGN KEY (committee_id) REFERENCES committees(committee_id)
);

CREATE TABLE committee_members (
    id SERIAL PRIMARY KEY,
    member_id VARCHAR(20) NOT NULL,
    committee_id VARCHAR(10) NOT NULL,
    subcommittee_id VARCHAR(10) NULL,
    role VARCHAR(50) NULL,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (committee_id) REFERENCES committees(committee_id),
    FOREIGN KEY (subcommittee_id) REFERENCES subcommittees(subcommittee_id)
);

-- Member Committees Table
CREATE TABLE member_committees (
    id SERIAL PRIMARY KEY,
    member_id VARCHAR(255),
    committee_id VARCHAR(10) NULL,
    committee_name VARCHAR(255),
    committee_code VARCHAR(10),
    committee_api_uri VARCHAR(255),
    committee_side VARCHAR(10),
    committee_title VARCHAR(255),
    rank_in_party INTEGER,
    committee_begin_date DATE NULL,
    committee_end_date DATE NULL,
    bill_id VARCHAR(20) NULL,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (committee_id) REFERENCES committees(committee_id)
);

-- Member Subcommittees Table
CREATE TABLE member_subcommittees (
    id SERIAL PRIMARY KEY,
    subcommittee_id VARCHAR(10) NULL,
    subcommittee_name VARCHAR(255),
    subcommittee_code VARCHAR(10),
    subcommittee_parent_committee_id VARCHAR(10),
    subcommittee_api_uri VARCHAR(255),
    subcommittee_side VARCHAR(10),
    subcommittee_title VARCHAR(255),
    subcommittee_rank_in_party INTEGER,
    subcommittee_begin_date DATE NULL,
    subcommittee_end_date DATE NULL,
    bill_id VARCHAR(20) NULL,
    FOREIGN KEY (subcommittee_id) REFERENCES subcommittees(subcommittee_id)
);

-- Bills Table
CREATE TABLE bills (
    bill_id VARCHAR(20) PRIMARY KEY,
    congress INT,
    chamber VARCHAR(10),
    bill_type VARCHAR(10),
    number VARCHAR(20),
    bill_uri VARCHAR(255) NULL,
    title TEXT,
    short_title TEXT,
    sponsor_title VARCHAR(50) NULL,
    sponsor_id VARCHAR(20),
    sponsor_name VARCHAR(100),
    sponsor_state CHAR(2),
    sponsor_party CHAR(2),
    sponsor_uri VARCHAR(255) NULL,
    gpo_pdf_uri VARCHAR(255) NULL,
    congressdotgov_url VARCHAR(255) NULL,
    govtrack_url VARCHAR(255) NULL,
    introduced_date DATE,
    active BOOLEAN,
    last_vote DATE NULL,
    house_passage DATE NULL,
    senate_passage DATE NULL,
    enacted DATE NULL,
    vetoed DATE NULL,
    cosponsors INT,
    primary_subject VARCHAR(100) NULL,
    summary TEXT NULL,
    summary_short TEXT NULL,
    latest_major_action_date DATE NULL,
    latest_major_action TEXT NULL
);

-- Cosponsors by Party Table
CREATE TABLE cosponsors_by_party (
    bill_id VARCHAR(20),
    party CHAR(2),
    count INT,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

-- Bill Committees Table
CREATE TABLE bill_committees (
    bill_id VARCHAR(20),
    committee_code VARCHAR(10),
    committee_name VARCHAR(255) NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

-- Bill Subcommittees Table
CREATE TABLE bill_subcommittees (
    bill_id VARCHAR(20),
    subcommittee_code VARCHAR(10),
    subcommittee_name VARCHAR(255) NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

-- Votes Table
CREATE TABLE votes (
    vote_id SERIAL PRIMARY KEY,
    congress INTEGER,
    session INTEGER,
    chamber VARCHAR(10),
    roll_call INTEGER,
    bill_id VARCHAR(20) NULL,  -- Link to bills table
    question TEXT,
    description TEXT,
    vote_type VARCHAR(20),
    date DATE,
    result VARCHAR(50),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

-- Member Votes Table
CREATE TABLE member_votes (
    member_vote_id SERIAL PRIMARY KEY,
    vote_id INTEGER,
    member_id VARCHAR(20),
    vote_position VARCHAR(20),
    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
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