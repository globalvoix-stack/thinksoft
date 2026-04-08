-- 002: Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    industry TEXT,
    mode TEXT NOT NULL DEFAULT 'autonomous'
        CHECK (mode IN ('light', 'autonomous', 'max')),
    design_tokens JSONB DEFAULT '{}'::jsonb,
    component_registry JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at DESC);
