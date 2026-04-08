"""Job queries — raw SQL, typed dataclasses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg


@dataclass
class Job:
    id: UUID
    project_id: UUID
    session_id: UUID
    mode: str
    status: str
    progress: int
    current_step: str | None
    prompt: str
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    metadata: dict[str, Any] = field(default_factory=dict)


def _row(record: asyncpg.Record) -> Job:
    d = dict(record)
    if isinstance(d.get("result"), str):
        d["result"] = json.loads(d["result"])
    raw_meta = d.get("metadata")
    if isinstance(raw_meta, str):
        d["metadata"] = json.loads(raw_meta)
    elif raw_meta is None:
        d["metadata"] = {}
    return Job(**d)


async def create_job(
    conn: asyncpg.Connection,
    project_id: UUID,
    session_id: UUID,
    mode: str,
    *,
    prompt: str = "",
    metadata: dict[str, Any] | None = None,
) -> Job:
    row = await conn.fetchrow(
        """
        INSERT INTO jobs (project_id, session_id, mode, prompt, metadata)
        VALUES ($1, $2, $3, $4, $5::jsonb)
        RETURNING *
        """,
        project_id, session_id, mode, prompt, json.dumps(metadata or {}),
    )
    return _row(row)


async def get_job(conn: asyncpg.Connection, job_id: UUID) -> Job | None:
    row = await conn.fetchrow("SELECT * FROM jobs WHERE id = $1", job_id)
    return _row(row) if row else None


async def get_job_for_project(
    conn: asyncpg.Connection, job_id: UUID, project_id: UUID
) -> Job | None:
    row = await conn.fetchrow(
        "SELECT * FROM jobs WHERE id = $1 AND project_id = $2",
        job_id, project_id,
    )
    return _row(row) if row else None


async def list_project_jobs(
    conn: asyncpg.Connection, project_id: UUID, *, limit: int = 20
) -> list[Job]:
    rows = await conn.fetch(
        "SELECT * FROM jobs WHERE project_id = $1 ORDER BY created_at DESC LIMIT $2",
        project_id, limit,
    )
    return [_row(r) for r in rows]


async def mark_job_running(conn: asyncpg.Connection, job_id: UUID) -> Job | None:
    """Transition job to running. Returns updated Job or None if not found."""
    row = await conn.fetchrow(
        """
        UPDATE jobs SET status = 'running'
        WHERE id = $1
        RETURNING *
        """,
        job_id,
    )
    return _row(row) if row else None


async def update_job_progress(
    conn: asyncpg.Connection,
    job_id: UUID,
    progress: int,
    current_step: str = "",
) -> None:
    await conn.execute(
        "UPDATE jobs SET progress = $1, current_step = $2 WHERE id = $3",
        progress, current_step or None, job_id,
    )


async def complete_job(
    conn: asyncpg.Connection, job_id: UUID, result: dict[str, Any]
) -> Job | None:
    row = await conn.fetchrow(
        """
        UPDATE jobs
        SET status = 'done', progress = 100, result = $1::jsonb, completed_at = now()
        WHERE id = $2
        RETURNING *
        """,
        json.dumps(result), job_id,
    )
    return _row(row) if row else None


async def fail_job(conn: asyncpg.Connection, job_id: UUID, error: str) -> Job | None:
    row = await conn.fetchrow(
        """
        UPDATE jobs
        SET status = 'failed', error = $1, completed_at = now()
        WHERE id = $2
        RETURNING *
        """,
        error, job_id,
    )
    return _row(row) if row else None


async def timeout_stale_jobs(conn: asyncpg.Connection, timeout_seconds: int = 300) -> int:
    """Mark running jobs that exceed the timeout as failed. Returns count."""
    result = await conn.execute(
        """
        UPDATE jobs
        SET status = 'failed',
            error = 'Job timed out after exceeding maximum execution time',
            completed_at = now()
        WHERE status = 'running'
          AND updated_at < now() - ($1 || ' seconds')::INTERVAL
        """,
        str(timeout_seconds),
    )
    return int(result.split()[-1])
