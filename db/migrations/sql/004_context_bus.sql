-- 004: Context bus snapshots
CREATE TABLE IF NOT EXISTS context_bus_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_context_project ON context_bus_snapshots(project_id);
CREATE INDEX IF NOT EXISTS idx_context_session ON context_bus_snapshots(session_id);
CREATE INDEX IF NOT EXISTS idx_context_latest
    ON context_bus_snapshots(project_id, created_at DESC);
