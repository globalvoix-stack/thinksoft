-- 009: Add session_id and metadata to memory_entries
ALTER TABLE memory_entries
    ADD COLUMN IF NOT EXISTS session_id UUID,
    ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_memory_session
    ON memory_entries(session_id) WHERE active = true;
