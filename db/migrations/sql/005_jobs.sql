-- 005: Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    session_id UUID NOT NULL DEFAULT gen_random_uuid(),
    mode TEXT NOT NULL
        CHECK (mode IN ('light', 'autonomous', 'max')),
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'done', 'failed')),
    progress INTEGER DEFAULT 0
        CHECK (progress >= 0 AND progress <= 100),
    current_step TEXT,
    prompt TEXT NOT NULL,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_jobs_project ON jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
    WHERE status IN ('queued', 'running');
CREATE INDEX IF NOT EXISTS idx_jobs_session ON jobs(session_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);
