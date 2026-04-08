-- 010: Add metadata to jobs table
ALTER TABLE jobs
    ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}';
