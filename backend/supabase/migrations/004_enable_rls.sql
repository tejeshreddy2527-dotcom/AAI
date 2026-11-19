-- ============================================
-- Migration 004: Enable Row Level Security (RLS) & Policies
-- ============================================

-- Enable RLS on all tables
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Allow read & write for anon/authenticated users (open chatbot)
-- messages
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'messages' AND policyname = 'Allow full access to messages'
    ) THEN
        CREATE POLICY "Allow full access to messages"
        ON messages FOR ALL
        USING (true) WITH CHECK (true);
    END IF;
END
$$;

-- sessions
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'sessions' AND policyname = 'Allow full access to sessions'
    ) THEN
        CREATE POLICY "Allow full access to sessions"
        ON sessions FOR ALL
        USING (true) WITH CHECK (true);
    END IF;
END
$$;

-- feedback
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'feedback' AND policyname = 'Allow full access to feedback'
    ) THEN
        CREATE POLICY "Allow full access to feedback"
        ON feedback FOR ALL
        USING (true) WITH CHECK (true);
    END IF;
END
$$;
