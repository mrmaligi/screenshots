# Australian Visa Tracking Application Data Architecture

## Phase 1: The Relational Database Architecture

Here is the absolute full SQL database schema for the application:

```sql

-- ==============================================================================
-- PHASE 1: RELATIONAL DATABASE ARCHITECTURE (PostgreSQL)
-- ==============================================================================

CREATE TABLE Users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    nationality VARCHAR(100),
    passport_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Visa_Catalogue (
    visa_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subclass_number VARCHAR(10) NOT NULL,
    visa_name VARCHAR(255) NOT NULL,
    stream_name VARCHAR(255),
    category VARCHAR(50) NOT NULL CHECK (category IN ('Temporary', 'Provisional', 'Permanent')),
    base_cost_aud NUMERIC(10, 2),
    points_tested BOOLEAN NOT NULL DEFAULT FALSE,
    requires_sponsor BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (subclass_number, stream_name)
);

CREATE TABLE ANZSCO_Master_List (
    anzsco_code VARCHAR(10) PRIMARY KEY,
    occupation_title VARCHAR(255) NOT NULL,
    assessing_authority VARCHAR(255),
    eligible_lists JSONB, -- Array of strings e.g., ["MLTSSL", "STSOL", "ROL"]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Points_Calculator (
    points_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    visa_id UUID NOT NULL REFERENCES Visa_Catalogue(visa_id) ON DELETE CASCADE,
    age_points INT DEFAULT 0,
    english_points INT DEFAULT 0,
    skilled_employment_points INT DEFAULT 0,
    qualifications_points INT DEFAULT 0,
    australian_study_points INT DEFAULT 0,
    specialist_education_points INT DEFAULT 0,
    regional_study_points INT DEFAULT 0,
    credentialled_community_language_points INT DEFAULT 0,
    py_points INT DEFAULT 0,
    partner_points INT DEFAULT 0,
    state_nomination_points INT DEFAULT 0,
    total_points INT DEFAULT 0,
    last_calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, visa_id)
);

CREATE TABLE Application_Stages (
    stage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visa_id UUID NOT NULL REFERENCES Visa_Catalogue(visa_id) ON DELETE CASCADE,
    stage_order INT NOT NULL,
    stage_name VARCHAR(255) NOT NULL,
    description TEXT,
    estimated_time_days INT,
    requires_action BOOLEAN DEFAULT FALSE,
    UNIQUE (visa_id, stage_order)
);

CREATE TABLE User_Journeys (
    journey_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    visa_id UUID NOT NULL REFERENCES Visa_Catalogue(visa_id) ON DELETE CASCADE,
    current_stage_id UUID REFERENCES Application_Stages(stage_id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Planning', 'In Progress', 'Lodged', 'Granted', 'Refused', 'Withdrawn')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    target_lodgement_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Document_Vault (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    journey_id UUID REFERENCES User_Journeys(journey_id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    file_url VARCHAR(255),
    issue_date DATE,
    expiry_date DATE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Missing', 'Uploaded', 'Verified', 'Expired')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_journeys_user_id ON User_Journeys(user_id);
CREATE INDEX idx_user_journeys_visa_id ON User_Journeys(visa_id);
CREATE INDEX idx_document_vault_user_id ON Document_Vault(user_id);
CREATE INDEX idx_document_vault_expiry ON Document_Vault(expiry_date);
```

## Phase 2: The Complete Visa Catalogue Data

Here is the exhaustive list of current Australian Visa Subclasses:

```json
[
    {
        "subclass_number": "189",
        "visa_name": "Skilled Independent",
        "stream_name": "Points-tested",
        "category": "Permanent",
        "base_cost_aud": 4710.0,
        "points_tested": true,
        "requires_sponsor": false
    },
    {
        "subclass_number": "189",
        "visa_name": "Skilled Independent",
        "stream_name": "New Zealand",
        "category": "Permanent",
        "base_cost_aud": 4710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "190",
        "visa_name": "Skilled Nominated",
        "stream_name": "State Nominated",
        "category": "Permanent",
        "base_cost_aud": 4710.0,
        "points_tested": true,
        "requires_sponsor": false
    },
    {
        "subclass_number": "491",
        "visa_name": "Skilled Work Regional (Provisional)",
        "stream_name": "State/Territory Sponsored",
        "category": "Provisional",
        "base_cost_aud": 4710.0,
        "points_tested": true,
        "requires_sponsor": false
    },
    {
        "subclass_number": "491",
        "visa_name": "Skilled Work Regional (Provisional)",
        "stream_name": "Family Sponsored",
        "category": "Provisional",
        "base_cost_aud": 4710.0,
        "points_tested": true,
        "requires_sponsor": true
    },
    {
        "subclass_number": "482",
        "visa_name": "Temporary Skill Shortage",
        "stream_name": "Short-term",
        "category": "Temporary",
        "base_cost_aud": 1495.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "482",
        "visa_name": "Temporary Skill Shortage",
        "stream_name": "Medium-term",
        "category": "Temporary",
        "base_cost_aud": 3115.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "482",
        "visa_name": "Temporary Skill Shortage",
        "stream_name": "Labour Agreement",
        "category": "Temporary",
        "base_cost_aud": 3115.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "186",
        "visa_name": "Employer Nomination Scheme",
        "stream_name": "Direct Entry",
        "category": "Permanent",
        "base_cost_aud": 4710.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "186",
        "visa_name": "Employer Nomination Scheme",
        "stream_name": "Temporary Residence Transition",
        "category": "Permanent",
        "base_cost_aud": 4710.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "186",
        "visa_name": "Employer Nomination Scheme",
        "stream_name": "Labour Agreement",
        "category": "Permanent",
        "base_cost_aud": 4710.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "494",
        "visa_name": "Skilled Employer Sponsored Regional (Provisional)",
        "stream_name": "Employer Sponsored",
        "category": "Provisional",
        "base_cost_aud": 4710.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "494",
        "visa_name": "Skilled Employer Sponsored Regional (Provisional)",
        "stream_name": "Labour Agreement",
        "category": "Provisional",
        "base_cost_aud": 4710.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "820",
        "visa_name": "Partner (Temporary)",
        "stream_name": "Onshore",
        "category": "Provisional",
        "base_cost_aud": 9095.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "801",
        "visa_name": "Partner (Permanent)",
        "stream_name": "Onshore",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "309",
        "visa_name": "Partner (Provisional)",
        "stream_name": "Offshore",
        "category": "Provisional",
        "base_cost_aud": 9095.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "100",
        "visa_name": "Partner (Migrant)",
        "stream_name": "Offshore",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "300",
        "visa_name": "Prospective Marriage",
        "stream_name": "Offshore",
        "category": "Provisional",
        "base_cost_aud": 9095.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "500",
        "visa_name": "Student",
        "stream_name": "Higher Education",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "500",
        "visa_name": "Student",
        "stream_name": "VET",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "500",
        "visa_name": "Student",
        "stream_name": "ELICOS",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "500",
        "visa_name": "Student",
        "stream_name": "Schools",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "500",
        "visa_name": "Student",
        "stream_name": "Non-Award",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "500",
        "visa_name": "Student",
        "stream_name": "Postgraduate Research",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "590",
        "visa_name": "Student Guardian",
        "stream_name": "Guardian",
        "category": "Temporary",
        "base_cost_aud": 710.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "485",
        "visa_name": "Temporary Graduate",
        "stream_name": "Post-Study Work",
        "category": "Temporary",
        "base_cost_aud": 1895.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "485",
        "visa_name": "Temporary Graduate",
        "stream_name": "Graduate Work",
        "category": "Temporary",
        "base_cost_aud": 1895.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "485",
        "visa_name": "Temporary Graduate",
        "stream_name": "Second Post-Study Work",
        "category": "Temporary",
        "base_cost_aud": 745.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "600",
        "visa_name": "Visitor",
        "stream_name": "Tourist (Onshore)",
        "category": "Temporary",
        "base_cost_aud": 425.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "600",
        "visa_name": "Visitor",
        "stream_name": "Tourist (Offshore)",
        "category": "Temporary",
        "base_cost_aud": 195.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "600",
        "visa_name": "Visitor",
        "stream_name": "Sponsored Family",
        "category": "Temporary",
        "base_cost_aud": 195.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "600",
        "visa_name": "Visitor",
        "stream_name": "Business Visitor",
        "category": "Temporary",
        "base_cost_aud": 195.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "600",
        "visa_name": "Visitor",
        "stream_name": "Approved Destination Status",
        "category": "Temporary",
        "base_cost_aud": 195.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "600",
        "visa_name": "Visitor",
        "stream_name": "Frequent Traveller",
        "category": "Temporary",
        "base_cost_aud": 1395.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "651",
        "visa_name": "eVisitor",
        "stream_name": "eVisitor",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "601",
        "visa_name": "Electronic Travel Authority",
        "stream_name": "ETA",
        "category": "Temporary",
        "base_cost_aud": 20.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "417",
        "visa_name": "Working Holiday",
        "stream_name": "Working Holiday",
        "category": "Temporary",
        "base_cost_aud": 635.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "462",
        "visa_name": "Work and Holiday",
        "stream_name": "Work and Holiday",
        "category": "Temporary",
        "base_cost_aud": 635.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Special Program",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Religious Work",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Research",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Invited Participant",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Sporting",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Entertainment",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Superyacht Crew",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Exchange",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Australian Government Endorsed Event",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "408",
        "visa_name": "Temporary Activity",
        "stream_name": "Domestic Worker (Executive)",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "400",
        "visa_name": "Temporary Work (Short Stay Specialist)",
        "stream_name": "Highly Specialised Work",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "403",
        "visa_name": "Temporary Work (International Relations)",
        "stream_name": "Government Agreement",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "403",
        "visa_name": "Temporary Work (International Relations)",
        "stream_name": "Foreign Government Agency",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "403",
        "visa_name": "Temporary Work (International Relations)",
        "stream_name": "Domestic Worker (Diplomatic or Consular)",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "403",
        "visa_name": "Temporary Work (International Relations)",
        "stream_name": "Privileges and Immunities",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "403",
        "visa_name": "Temporary Work (International Relations)",
        "stream_name": "Pacific Australia Labour Mobility",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "407",
        "visa_name": "Training",
        "stream_name": "Occupational Training",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "188",
        "visa_name": "Business Innovation and Investment (Provisional)",
        "stream_name": "Business Innovation",
        "category": "Provisional",
        "base_cost_aud": 6270.0,
        "points_tested": true,
        "requires_sponsor": false
    },
    {
        "subclass_number": "188",
        "visa_name": "Business Innovation and Investment (Provisional)",
        "stream_name": "Investor",
        "category": "Provisional",
        "base_cost_aud": 6270.0,
        "points_tested": true,
        "requires_sponsor": false
    },
    {
        "subclass_number": "188",
        "visa_name": "Business Innovation and Investment (Provisional)",
        "stream_name": "Significant Investor",
        "category": "Provisional",
        "base_cost_aud": 9455.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "188",
        "visa_name": "Business Innovation and Investment (Provisional)",
        "stream_name": "Premium Investor",
        "category": "Provisional",
        "base_cost_aud": 10255.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "188",
        "visa_name": "Business Innovation and Investment (Provisional)",
        "stream_name": "Entrepreneur",
        "category": "Provisional",
        "base_cost_aud": 4240.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "888",
        "visa_name": "Business Innovation and Investment (Permanent)",
        "stream_name": "Business Innovation",
        "category": "Permanent",
        "base_cost_aud": 3025.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "888",
        "visa_name": "Business Innovation and Investment (Permanent)",
        "stream_name": "Investor",
        "category": "Permanent",
        "base_cost_aud": 3025.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "888",
        "visa_name": "Business Innovation and Investment (Permanent)",
        "stream_name": "Significant Investor",
        "category": "Permanent",
        "base_cost_aud": 3025.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "888",
        "visa_name": "Business Innovation and Investment (Permanent)",
        "stream_name": "Premium Investor",
        "category": "Permanent",
        "base_cost_aud": 3025.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "888",
        "visa_name": "Business Innovation and Investment (Permanent)",
        "stream_name": "Entrepreneur",
        "category": "Permanent",
        "base_cost_aud": 3025.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "132",
        "visa_name": "Business Talent (Permanent)",
        "stream_name": "Significant Business History",
        "category": "Permanent",
        "base_cost_aud": 7855.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "132",
        "visa_name": "Business Talent (Permanent)",
        "stream_name": "Venture Capital Entrepreneur",
        "category": "Permanent",
        "base_cost_aud": 7855.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "858",
        "visa_name": "Global Talent",
        "stream_name": "Global Talent",
        "category": "Permanent",
        "base_cost_aud": 4305.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "124",
        "visa_name": "Distinguished Talent",
        "stream_name": "Distinguished Talent",
        "category": "Permanent",
        "base_cost_aud": 4305.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "143",
        "visa_name": "Contributory Parent",
        "stream_name": "Contributory Parent",
        "category": "Permanent",
        "base_cost_aud": 47975.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "173",
        "visa_name": "Contributory Parent (Temporary)",
        "stream_name": "Contributory Parent",
        "category": "Temporary",
        "base_cost_aud": 32340.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "864",
        "visa_name": "Contributory Aged Parent",
        "stream_name": "Contributory Aged Parent",
        "category": "Permanent",
        "base_cost_aud": 47975.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "884",
        "visa_name": "Contributory Aged Parent (Temporary)",
        "stream_name": "Contributory Aged Parent",
        "category": "Temporary",
        "base_cost_aud": 32340.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "103",
        "visa_name": "Parent",
        "stream_name": "Parent",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "804",
        "visa_name": "Aged Parent",
        "stream_name": "Aged Parent",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "870",
        "visa_name": "Sponsored Parent (Temporary)",
        "stream_name": "Sponsored Parent",
        "category": "Temporary",
        "base_cost_aud": 5735.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "101",
        "visa_name": "Child",
        "stream_name": "Child",
        "category": "Permanent",
        "base_cost_aud": 3055.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "802",
        "visa_name": "Child",
        "stream_name": "Child",
        "category": "Permanent",
        "base_cost_aud": 3055.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "102",
        "visa_name": "Adoption",
        "stream_name": "Adoption",
        "category": "Permanent",
        "base_cost_aud": 3055.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "445",
        "visa_name": "Dependent Child",
        "stream_name": "Dependent Child",
        "category": "Temporary",
        "base_cost_aud": 3055.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "114",
        "visa_name": "Aged Dependent Relative",
        "stream_name": "Aged Dependent Relative",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "838",
        "visa_name": "Aged Dependent Relative",
        "stream_name": "Aged Dependent Relative",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "115",
        "visa_name": "Remaining Relative",
        "stream_name": "Remaining Relative",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "835",
        "visa_name": "Remaining Relative",
        "stream_name": "Remaining Relative",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "116",
        "visa_name": "Carer",
        "stream_name": "Carer",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "836",
        "visa_name": "Carer",
        "stream_name": "Carer",
        "category": "Permanent",
        "base_cost_aud": 4990.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "117",
        "visa_name": "Orphan Relative",
        "stream_name": "Orphan Relative",
        "category": "Permanent",
        "base_cost_aud": 1810.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "837",
        "visa_name": "Orphan Relative",
        "stream_name": "Orphan Relative",
        "category": "Permanent",
        "base_cost_aud": 1810.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "151",
        "visa_name": "Former Resident",
        "stream_name": "Former Resident",
        "category": "Permanent",
        "base_cost_aud": 4240.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "155",
        "visa_name": "Resident Return",
        "stream_name": "Resident Return",
        "category": "Permanent",
        "base_cost_aud": 465.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "157",
        "visa_name": "Resident Return",
        "stream_name": "Resident Return",
        "category": "Permanent",
        "base_cost_aud": 465.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "159",
        "visa_name": "Provisional Resident Return",
        "stream_name": "Provisional Resident Return",
        "category": "Provisional",
        "base_cost_aud": 420.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "461",
        "visa_name": "New Zealand Citizen Family Relationship (Temporary)",
        "stream_name": "New Zealand Citizen Family Relationship",
        "category": "Temporary",
        "base_cost_aud": 405.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "444",
        "visa_name": "Special Category",
        "stream_name": "Special Category",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "010",
        "visa_name": "Bridging visa A",
        "stream_name": "BVA",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "020",
        "visa_name": "Bridging visa B",
        "stream_name": "BVB",
        "category": "Temporary",
        "base_cost_aud": 180.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "030",
        "visa_name": "Bridging visa C",
        "stream_name": "BVC",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "040",
        "visa_name": "Bridging visa D",
        "stream_name": "BVD",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "041",
        "visa_name": "Bridging visa D",
        "stream_name": "BVD",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "050",
        "visa_name": "Bridging visa E",
        "stream_name": "BVE",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "051",
        "visa_name": "Bridging visa E",
        "stream_name": "BVE",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "060",
        "visa_name": "Bridging visa F",
        "stream_name": "BVF",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "771",
        "visa_name": "Transit",
        "stream_name": "Transit",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "988",
        "visa_name": "Maritime Crew",
        "stream_name": "Maritime Crew",
        "category": "Temporary",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "200",
        "visa_name": "Refugee",
        "stream_name": "Refugee",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "201",
        "visa_name": "In-country Special Humanitarian",
        "stream_name": "In-country Special Humanitarian",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "202",
        "visa_name": "Global Special Humanitarian",
        "stream_name": "Global Special Humanitarian",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": true
    },
    {
        "subclass_number": "203",
        "visa_name": "Emergency Rescue",
        "stream_name": "Emergency Rescue",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "204",
        "visa_name": "Woman at Risk",
        "stream_name": "Woman at Risk",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "866",
        "visa_name": "Protection",
        "stream_name": "Protection",
        "category": "Permanent",
        "base_cost_aud": 45.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "785",
        "visa_name": "Temporary Protection",
        "stream_name": "Temporary Protection",
        "category": "Temporary",
        "base_cost_aud": 45.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "790",
        "visa_name": "Safe Haven Enterprise",
        "stream_name": "Safe Haven Enterprise",
        "category": "Temporary",
        "base_cost_aud": 45.0,
        "points_tested": false,
        "requires_sponsor": false
    },
    {
        "subclass_number": "851",
        "visa_name": "Resolution of Status",
        "stream_name": "Resolution of Status",
        "category": "Permanent",
        "base_cost_aud": 0.0,
        "points_tested": false,
        "requires_sponsor": false
    }
]
```

## Phase 3 & 4 Acknowledgement

I am ready for Phase 3 (The ANZSCO Master List) and Phase 4 (Application Lifecycles).

---

Are you ready for 'Phase 3: Batch 1'?
