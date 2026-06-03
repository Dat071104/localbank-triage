CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(64) UNIQUE NOT NULL,
    customer_text TEXT NOT NULL,
    status VARCHAR(32),
    created_by VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ticket_analysis (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(64) UNIQUE REFERENCES tickets(ticket_id),
    classification JSONB,
    urgency JSONB,
    created_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS retrieved_evidence (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(64) REFERENCES tickets(ticket_id),
    policy_id VARCHAR(64),
    chunk_id VARCHAR(256),
    title VARCHAR(256),
    section VARCHAR(128),
    score DOUBLE PRECISION,
    text TEXT,
    item_metadata JSONB
);

CREATE TABLE IF NOT EXISTS drafts (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(64) REFERENCES tickets(ticket_id),
    draft JSONB,
    edited_draft_response TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS review_actions (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(64),
    employee_id VARCHAR(64),
    role VARCHAR(32),
    action VARCHAR(32),
    comment TEXT,
    created_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS workflow_audit_logs (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(64) REFERENCES tickets(ticket_id),
    actor_employee_id VARCHAR(64),
    actor_role VARCHAR(32),
    action VARCHAR(64),
    status VARCHAR(32),
    details JSONB,
    created_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS worker_job_results (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(128) UNIQUE NOT NULL,
    ticket_id VARCHAR(64),
    status VARCHAR(32),
    result JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
