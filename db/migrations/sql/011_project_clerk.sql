-- 011: Add Clerk user ID string, is_starred, image_url to projects
-- user_id was UUID; Clerk IDs are text like 'user_2abc...'
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS clerk_user_id TEXT,
    ADD COLUMN IF NOT EXISTS is_starred    BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS image_url     TEXT;

CREATE INDEX IF NOT EXISTS idx_projects_clerk_user
    ON projects(clerk_user_id);
