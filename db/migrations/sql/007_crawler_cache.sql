-- 007: Crawler cache with 72h TTL
CREATE TABLE IF NOT EXISTS crawler_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    industry TEXT,
    screenshots JSONB DEFAULT '[]'::jsonb,
    tech_stack JSONB DEFAULT '{}'::jsonb,
    cached_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ DEFAULT now() + INTERVAL '72 hours'
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_crawler_url ON crawler_cache(url);
CREATE INDEX IF NOT EXISTS idx_crawler_industry ON crawler_cache(industry);
CREATE INDEX IF NOT EXISTS idx_crawler_expires ON crawler_cache(expires_at);
