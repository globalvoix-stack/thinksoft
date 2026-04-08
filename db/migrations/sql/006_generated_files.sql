-- 006: Generated files
CREATE TABLE IF NOT EXISTS generated_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    language TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(project_id, file_path)
);

CREATE INDEX IF NOT EXISTS idx_files_project ON generated_files(project_id);
CREATE INDEX IF NOT EXISTS idx_files_job ON generated_files(job_id);
CREATE INDEX IF NOT EXISTS idx_files_path ON generated_files(project_id, file_path);
