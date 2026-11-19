-- ============================================
-- Migration 002: Create sessions table
-- Tracks individual chat sessions / conversations
-- ============================================

CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::TEXT, NOW()) NOT NULL,
    title       TEXT DEFAULT 'New Chat',
    is_active   BOOLEAN DEFAULT TRUE
);

-- Index for listing active sessions
CREATE INDEX IF NOT EXISTS idx_sessions_active
    ON sessions (is_active, updated_at DESC);

COMMENT ON TABLE sessions IS 'Tracks individual chat sessions';
