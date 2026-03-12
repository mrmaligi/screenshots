import json

def generate_sql():
    sql = """
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
"""
    return sql

with open('visa_schema.sql', 'w') as f:
    f.write(generate_sql())
