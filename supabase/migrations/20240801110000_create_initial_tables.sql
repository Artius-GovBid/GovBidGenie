CREATE TABLE opportunities (
    id SERIAL PRIMARY KEY,
    sam_gov_id VARCHAR(255) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    agency VARCHAR(255),
    location_text VARCHAR(255),
    url VARCHAR(2048),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    posted_date TIMESTAMPTZ
);

CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    source VARCHAR,
    status VARCHAR DEFAULT 'Identified',
    azure_devops_work_item_id INTEGER,
    business_name VARCHAR,
    facebook_page_url VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    opportunity_id INTEGER REFERENCES opportunities(id)
);

CREATE TABLE conversation_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    sender VARCHAR,
    message TEXT,
    lead_id INTEGER REFERENCES leads(id)
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    title VARCHAR,
    status VARCHAR DEFAULT 'tentative',
    external_event_id VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    lead_id INTEGER REFERENCES leads(id)
);

CREATE TABLE learnings (
    id SERIAL PRIMARY KEY,
    outcome_tag VARCHAR,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    conversation_id INTEGER REFERENCES conversation_logs(id)
); 