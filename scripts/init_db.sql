-- PostgreSQL initialization script for AI Health Insurance Cold Calling Agent
-- Run: psql -U postgres -f init_db.sql

\c insurance_cold_calling;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Lead status enum
CREATE TYPE lead_status AS ENUM (
    'pending', 'called', 'interested', 'not_interested',
    'callback', 'busy', 'wrong_number', 'dnc'
);

-- Campaign status enum
CREATE TYPE campaign_status AS ENUM (
    'draft', 'active', 'paused', 'completed'
);

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'urdu',
    status lead_status NOT NULL DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    assigned_campaign_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_leads_phone ON leads(phone);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_campaign ON leads(assigned_campaign_id);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    script_template TEXT NOT NULL,
    greeting_message TEXT,
    closing_message TEXT,
    status campaign_status NOT NULL DEFAULT 'draft',
    total_leads INTEGER NOT NULL DEFAULT 0,
    processed_leads INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Call logs table
CREATE TABLE IF NOT EXISTS call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id),
    campaign_id UUID REFERENCES campaigns(id),
    duration_seconds INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'initiated',
    transcript JSONB DEFAULT '[]',
    summary TEXT,
    sentiment_score FLOAT,
    lead_status VARCHAR(20),
    recording_path VARCHAR(500),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_call_logs_lead ON call_logs(lead_id);
CREATE INDEX idx_call_logs_campaign ON call_logs(campaign_id);
CREATE INDEX idx_call_logs_created ON call_logs(created_at);

-- Knowledge base table for RAG (simple text-based, no vector extension needed)
CREATE TABLE IF NOT EXISTS insurance_knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
