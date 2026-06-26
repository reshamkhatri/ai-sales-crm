-- Core schema for the AI Sales Assistant

-- Leads / Prospects
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    business_name TEXT,
    phone TEXT,
    email TEXT,
    source TEXT, -- facebook, instagram, linkedin, email, referral, manual
    status TEXT DEFAULT 'new', -- new, contacted, qualified, proposal, negotiation, won, lost
    score INTEGER DEFAULT 0, -- 0-100
    notes TEXT,
    location TEXT,
    industry TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages (from all platforms)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    platform TEXT, -- facebook, instagram, linkedin, email, whatsapp, twitter
    content TEXT,
    sender TEXT, -- lead or assistant or user
    ai_analyzed INTEGER DEFAULT 0,
    extracted_data TEXT, -- JSON string: budget, timeline, needs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Ad Campaigns (Meta)
CREATE TABLE IF NOT EXISTS ad_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meta_campaign_id TEXT UNIQUE,
    meta_adset_id TEXT,
    meta_ad_id TEXT,
    name TEXT,
    objective TEXT,
    status TEXT,
    daily_budget REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ad Insights (daily snapshots)
CREATE TABLE IF NOT EXISTS ad_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    date TEXT,
    spend REAL,
    impressions INTEGER,
    clicks INTEGER,
    ctr REAL,
    cpm REAL,
    cpc REAL,
    leads INTEGER,
    messaging_conversations INTEGER,
    cost_per_lead REAL,
    reach INTEGER,
    frequency REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES ad_campaigns(id)
);

-- AI Recommendations
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT, -- ad_analysis, lead_strategy, follow_up, meeting_suggestion
    content TEXT,
    data_snapshot TEXT,
    actioned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meetings
CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    suggested_by_ai INTEGER DEFAULT 0,
    meeting_date TEXT,
    location TEXT,
    outcome TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Cold Calls
CREATE TABLE IF NOT EXISTS cold_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    phone TEXT,
    script TEXT,
    notes TEXT,
    called_at TIMESTAMP,
    result TEXT, -- answered, no_answer, voicemail, callback, not_interested
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Outbound Drafts (AI generated, waiting for user to send)
CREATE TABLE IF NOT EXISTS outbound_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    platform TEXT, -- linkedin, email, twitter, instagram, whatsapp, telegram, botim
    draft_text TEXT,
    sent INTEGER DEFAULT 0,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Business rules and preferences the AI copilot should remember
CREATE TABLE IF NOT EXISTS business_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_text TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CEO / team chat history with the business copilot
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    data_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated daily CEO briefs
CREATE TABLE IF NOT EXISTS daily_briefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brief_date TEXT UNIQUE,
    content TEXT NOT NULL,
    data_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Structured follow-up and work queue tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT DEFAULT 'follow_up',
    status TEXT DEFAULT 'open',
    priority INTEGER DEFAULT 3,
    due_date TEXT,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Prospecting search history & cache
CREATE TABLE IF NOT EXISTS prospect_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_type TEXT NOT NULL,          -- google_maps, web_search, csv_import
    query TEXT,                          -- search keywords
    location TEXT,                       -- target location
    result_count INTEGER DEFAULT 0,
    imported_count INTEGER DEFAULT 0,
    results_json TEXT,                   -- cached JSON results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
