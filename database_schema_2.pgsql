-- Congressional Members Table
CREATE TABLE CongressionalMembers (
    bioguideId VARCHAR(10) PRIMARY KEY,
    directOrderName VARCHAR(255),
    firstName VARCHAR(100),
    lastName VARCHAR(100),
    honorificName VARCHAR(50),
    invertedOrderName VARCHAR(255),
    birthYear INT,
    state VARCHAR(50),
    updateDate TIMESTAMP,
    imageUrl VARCHAR(255),
    depictionAttribution TEXT
);

-- Terms Table
CREATE TABLE Terms (
    termId INT AUTO_INCREMENT PRIMARY KEY,
    bioguideId VARCHAR(10),
    chamber VARCHAR(50),
    congress INT,
    startYear INT,
    endYear INT NULL,
    memberType VARCHAR(100),
    stateCode VARCHAR(10),
    stateName VARCHAR(100),
    FOREIGN KEY (bioguideId) REFERENCES CongressionalMembers(bioguideId)
);

-- Leadership Table
CREATE TABLE Leadership (
    leadershipId INT AUTO_INCREMENT PRIMARY KEY,
    bioguideId VARCHAR(10),
    congress INT,
    type VARCHAR(100),
    FOREIGN KEY (bioguideId) REFERENCES CongressionalMembers(bioguideId)
);

-- Party History Table
CREATE TABLE PartyHistory (
    partyHistoryId INT AUTO_INCREMENT PRIMARY KEY,
    bioguideId VARCHAR(10),
    partyAbbreviation VARCHAR(10),
    partyName VARCHAR(50),
    startYear INT,
    FOREIGN KEY (bioguideId) REFERENCES CongressionalMembers(bioguideId)
);

-- Sponsored Legislation Table
CREATE TABLE SponsoredLegislation (
    legislationId INT AUTO_INCREMENT PRIMARY KEY,
    bioguideId VARCHAR(10),
    congress INT,
    introducedDate DATE,
    actionDate DATE,
    actionText TEXT,
    number VARCHAR(50),
    policyAreaName VARCHAR(100),
    title TEXT,
    type VARCHAR(10),
    url VARCHAR(255),
    FOREIGN KEY (bioguideId) REFERENCES CongressionalMembers(bioguideId)
);

-- Cosponsored Legislation Table
CREATE TABLE CosponsoredLegislation (
    legislationId INT AUTO_INCREMENT PRIMARY KEY,
    bioguideId VARCHAR(10),
    congress INT,
    introducedDate DATE,
    actionDate DATE,
    actionText TEXT,
    number VARCHAR(50),
    policyAreaName VARCHAR(100),
    title TEXT,
    type VARCHAR(10),
    url VARCHAR(255),
    FOREIGN KEY (bioguideId) REFERENCES CongressionalMembers(bioguideId)
);

-- Committees Table
CREATE TABLE Committees (
    committeeId INT AUTO_INCREMENT PRIMARY KEY,
    chamber VARCHAR(50),
    committeeTypeCode VARCHAR(50),
    name VARCHAR(255),
    parent INT NULL,
    systemCode VARCHAR(10),
    url VARCHAR(255),
    isCurrent BOOLEAN,
    updateDate TIMESTAMP
);

-- Subcommittees Table
CREATE TABLE Subcommittees (
    subcommitteeId INT AUTO_INCREMENT PRIMARY KEY,
    committeeId INT,
    name VARCHAR(255),
    systemCode VARCHAR(10),
    url VARCHAR(255),
    FOREIGN KEY (committeeId) REFERENCES Committees(committeeId)
);

-- CommitteeHistory Table
CREATE TABLE CommitteeHistory (
    historyId INT AUTO_INCREMENT PRIMARY KEY,
    committeeId INT,
    libraryOfCongressName VARCHAR(255),
    officialName VARCHAR(255),
    startDate TIMESTAMP,
    endDate TIMESTAMP NULL,
    updateDate TIMESTAMP,
    FOREIGN KEY (committeeId) REFERENCES Committees(committeeId)
);

-- CommitteeBills Table
CREATE TABLE CommitteeBills (
    billId INT AUTO_INCREMENT PRIMARY KEY,
    committeeId INT,
    congress INT,
    billNumber VARCHAR(50),
    url VARCHAR(255),
    FOREIGN KEY (committeeId) REFERENCES Committees(committeeId)
);

-- CommitteeReports Table
CREATE TABLE CommitteeReports (
    reportId INT AUTO_INCREMENT PRIMARY KEY,
    committeeId INT,
    reportNumber VARCHAR(50),
    url VARCHAR(255),
    FOREIGN KEY (committeeId) REFERENCES Committees(committeeId)
);

-- CommitteeNominations Table
CREATE TABLE CommitteeNominations (
    nominationId INT AUTO_INCREMENT PRIMARY KEY,
    committeeId INT,
    nominationNumber VARCHAR(50),
    url VARCHAR(255),
    FOREIGN KEY (committeeId) REFERENCES Committees(committeeId)
);

-- CommitteeCommunications Table
CREATE TABLE CommitteeCommunications (
    communicationId INT AUTO_INCREMENT PRIMARY KEY,
    committeeId INT,
    chamber VARCHAR(50),
    communicationNumber VARCHAR(50),
    url VARCHAR(255),
    FOREIGN KEY (committeeId) REFERENCES Committees(committeeId)
);


-- Bills Table
CREATE TABLE Bills (
    billId INT AUTO_INCREMENT PRIMARY KEY,
    congress INT,
    number VARCHAR(10),
    originChamber VARCHAR(50),
    originChamberCode CHAR(1),
    title TEXT,
    type VARCHAR(10),
    updateDate TIMESTAMP,
    updateDateIncludingText TIMESTAMP,
    url VARCHAR(255)
);

-- BillActions Table
CREATE TABLE BillActions (
    actionId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    actionDate DATE,
    text TEXT,
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillAmendments Table
CREATE TABLE BillAmendments (
    amendmentId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    description TEXT,
    pubDate TIMESTAMP,
    title TEXT,
    url VARCHAR(255),
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillCommittees Table
CREATE TABLE BillCommittees (
    committeeId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    citation TEXT,
    url VARCHAR(255),
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillCosponsors Table
CREATE TABLE BillCosponsors (
    cosponsorId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    bioguideId VARCHAR(10),
    district INT,
    firstName VARCHAR(100),
    fullName VARCHAR(255),
    lastName VARCHAR(100),
    party VARCHAR(50),
    state VARCHAR(50),
    url VARCHAR(255),
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillRelatedBills Table
CREATE TABLE BillRelatedBills (
    relatedBillId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    relatedBillNumber VARCHAR(10),
    congress INT,
    type VARCHAR(10),
    url VARCHAR(255),
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillSubjects Table
CREATE TABLE BillSubjects (
    subjectId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    name VARCHAR(255),
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillSummaries Table
CREATE TABLE BillSummaries (
    summaryId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    text TEXT,
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillTextVersions Table
CREATE TABLE BillTextVersions (
    textVersionId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    versionText TEXT,
    url VARCHAR(255),
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);

-- BillTitles Table
CREATE TABLE BillTitles (
    titleId INT AUTO_INCREMENT PRIMARY KEY,
    billId INT,
    titleText TEXT,
    FOREIGN KEY (billId) REFERENCES Bills(billId)
);