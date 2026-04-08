"""Generated file queries — raw SQL, typed dataclasses."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import asyncpg


@dataclass
class GeneratedFile:
    id: UUID
    project_id: UUID
    job_id: UUID
    file_path: str
    content: str
    language: str | None
    version: int
    created_at: datetime
    updated_at: datetime


def _row(record: asyncpg.Record) -> GeneratedFile:
    return GeneratedFile(**dict(record))


async def upsert_file(
    conn: asyncpg.Connection,
    project_id: UUID,
    job_id: UUID,
    file_path: str,
    content: str,
    language: str | None,
) -> GeneratedFile:
    row = await conn.fetchrow(
        """
        INSERT INTO generated_files (project_id, job_id, file_path, content, language)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (project_id, file_path)
        DO UPDATE SET
            content = EXCLUDED.content,
            job_id = EXCLUDED.job_id,
            language = EXCLUDED.language,
            version = generated_files.version + 1,
            updated_at = now()
        RETURNING *
        """,
        project_id, job_id, file_path, content, language,
    )
    return _row(row)


async def get_file(
    conn: asyncpg.Connection, project_id: UUID, file_path: str
) -> GeneratedFile | None:
    row = await conn.fetchrow(
        "SELECT * FROM generated_files WHERE project_id = $1 AND file_path = $2",
        project_id, file_path,
    )
    return _row(row) if row else None


async def get_project_files(
    conn: asyncpg.Connection, project_id: UUID
) -> list[GeneratedFile]:
    rows = await conn.fetch(
        "SELECT * FROM generated_files WHERE project_id = $1 ORDER BY file_path",
        project_id,
    )
    return [_row(r) for r in rows]


async def get_job_files(
    conn: asyncpg.Connection, job_id: UUID
) -> list[GeneratedFile]:
    rows = await conn.fetch(
        "SELECT * FROM generated_files WHERE job_id = $1 ORDER BY file_path",
        job_id,
    )
    return [_row(r) for r in rows]


async def delete_project_files(conn: asyncpg.Connection, project_id: UUID) -> None:
    await conn.execute(
        "DELETE FROM generated_files WHERE project_id = $1", project_id
    )
