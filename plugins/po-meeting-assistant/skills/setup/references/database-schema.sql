-- ============================================================
-- PO Meeting Assistant — Database Schema (Config Only)
-- No message storage. All data is queried fresh via MCP.
-- Run this in Supabase SQL Editor (Database > SQL Editor)
-- ============================================================

-- ============================================================
-- Table 1: PO Preferences
-- One row per Product Owner.
-- ============================================================
CREATE TABLE IF NOT EXISTS po_preferences (
  po_id                       TEXT PRIMARY KEY,
  display_name                TEXT        NOT NULL,
  notification_slack_user_id  TEXT        NOT NULL,
  briefing_lead_minutes       INT         NOT NULL DEFAULT 10,
  time_window_days            INT         NOT NULL DEFAULT 14,
  metadata                    JSONB       NOT NULL DEFAULT '{}', -- internal flags (e.g. last briefing sent)
  created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Table 2: Clients
-- Maps each client to their data sources.
-- ============================================================
CREATE TABLE IF NOT EXISTS clients (
  id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  po_id                TEXT        NOT NULL REFERENCES po_preferences(po_id) ON DELETE CASCADE,
  client_id            TEXT        NOT NULL,
  display_name         TEXT        NOT NULL,
  email_domains        TEXT[]      NOT NULL DEFAULT '{}',
  calendar_keywords    TEXT[]      NOT NULL DEFAULT '{}',
  airtable_client_name TEXT,                -- exact Client Name value in Airtable OKR base (nullable)
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(po_id, client_id)
);

-- ============================================================
-- Table 3: Slack Channels
-- Which channels to query per client (or globally).
-- ============================================================
CREATE TABLE IF NOT EXISTS slack_channels (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  po_id        TEXT        NOT NULL REFERENCES po_preferences(po_id) ON DELETE CASCADE,
  channel_id   TEXT        NOT NULL,
  channel_name TEXT,
  client_id    TEXT,                 -- NULL if scope is 'global' or 'team'
  scope        TEXT        NOT NULL  DEFAULT 'client'
                           CHECK (scope IN ('client', 'global', 'team')),
  priority     INT         NOT NULL  DEFAULT 2
                           CHECK (priority BETWEEN 1 AND 3),
  UNIQUE(po_id, channel_id)
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_clients_po       ON clients       (po_id);
CREATE INDEX IF NOT EXISTS idx_channels_po_client ON slack_channels (po_id, client_id);
CREATE INDEX IF NOT EXISTS idx_channels_scope   ON slack_channels (po_id, scope);

-- ============================================================
-- Row Level Security (for shared multi-PO deployment)
-- Uncomment when using a single Supabase project for all POs.
-- ============================================================
-- ALTER TABLE po_preferences ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE clients        ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE slack_channels ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY po_preferences_isolation ON po_preferences  USING (po_id = current_setting('app.current_po_id', true));
-- CREATE POLICY clients_isolation         ON clients         USING (po_id = current_setting('app.current_po_id', true));
-- CREATE POLICY slack_channels_isolation  ON slack_channels  USING (po_id = current_setting('app.current_po_id', true));
