"""Crawler cache queries — raw SQL, typed dataclasses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg


@dataclass
class CrawlerCacheEntry:
    id: UUID
    url: str
    industry: str | None
    screenshots: list[Any]
    tech_stack: dict[str, Any]
    cached_at: datetime
    expires_at: datetime


def _row(record: asyncpg.Record) -> CrawlerCacheEntry:
    d = dict(record)
    for key in ("screenshots", "tech_stack"):
        raw = d.get(key)
        if isinstance(raw, str):
            d[key] = json.loads(raw)
        elif raw is None:
            d[key] = [] if key == "screenshots" else {}
    return CrawlerCacheEntry(**d)


async def get_cached(
    conn: asyncpg.Connection, url: str
) -> CrawlerCacheEntry | None:
    row = await conn.fetchrow(
        """
        SELECT * FROM crawler_cache
        WHERE url = $1 AND expires_at > now()
        """,
        url,
    )
    return _row(row) if row else None


async def upsert_cache(
    conn: asyncpg.Connection,
    url: str,
    industry: str | None,
    screenshots: list[Any],
    tech_stack: dict[str, Any],
) -> CrawlerCacheEntry:
    row = await conn.fetchrow(
        """
        INSERT INTO crawler_cache (url, industry, screenshots, tech_stack)
        VALUES ($1, $2, $3::jsonb, $4::jsonb)
        ON CONFLICT (url) DO UPDATE
        SET industry = EXCLUDED.industry,
            screenshots = EXCLUDED.screenshots,
            tech_stack = EXCLUDED.tech_stack,
            cached_at = now(),
            expires_at = now() + INTERVAL '72 hours'
        RETURNING *
        """,
        url, industry, json.dumps(screenshots), json.dumps(tech_stack),
    )
    return _row(row)


async def delete_expired(conn: asyncpg.Connection) -> int:
    result = await conn.execute(
        "DELETE FROM crawler_cache WHERE expires_at <= now()"
    )
    return int(result.split()[-1])
