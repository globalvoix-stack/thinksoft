-- 003: Memory entries with embedding support
CREATE TABLE IF NOT EXISTS memory_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    type TEXT NOT NULL
        CHECK (type IN ('constraint', 'preference', 'decision', 'component', 'style')),
    content TEXT NOT NULL,
    source TEXT NOT NULL
        CHECK (source IN ('user_explicit', 'user_implicit', 'agent_decision')),
    active BOOLEAN DEFAULT true,
    overridden_by UUID REFERENCES memory_entries(id),
    embedding JSONB,  -- Voyage AI embedding stored as JSON float array
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memory_project_active
    ON memory_entries(project_id) WHERE active = true;

CREATE INDEX IF NOT EXISTS idx_memory_type
    ON memory_entries(project_id, type) WHERE active = true;
