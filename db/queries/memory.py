"""Memory entry queries — raw SQL, typed dataclasses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg


@dataclass
class MemoryEntry:
    id: UUID
    project_id: UUID
    type: str
    content: str
    source: str
    active: bool
    overridden_by: UUID | None
    embedding: list[float] | None
    created_at: datetime
    session_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _row(record: asyncpg.Record) -> MemoryEntry:
    d = dict(record)
    raw_emb = d.get("embedding")
    if raw_emb is not None:
        d["embedding"] = json.loads(raw_emb) if isinstance(raw_emb, str) else raw_emb
    raw_meta = d.get("metadata")
    if isinstance(raw_meta, str):
        d["metadata"] = json.loads(raw_meta)
    elif raw_meta is None:
        d["metadata"] = {}
    return MemoryEntry(**d)


async def write_memory(
    conn: asyncpg.Connection,
    project_id: UUID,
    session_id: UUID | None,
    content: str,
    source: str,
    memory_type: str,
    embedding: list[float] | None = None,
    metadata: dict[str, Any] | None = None,
) -> MemoryEntry:
    row = await conn.fetchrow(
        """
        INSERT INTO memory_entries
            (project_id, session_id, type, content, source, embedding, metadata)
        VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb)
        RETURNING *
        """,
        project_id,
        session_id,
        memory_type,
        content,
        source,
        json.dumps(embedding) if embedding is not None else None,
        json.dumps(metadata or {}),
    )
    return _row(row)


async def get_entry(
    conn: asyncpg.Connection, entry_id: UUID
) -> MemoryEntry | None:
    row = await conn.fetchrow(
        "SELECT * FROM memory_entries WHERE id = $1", entry_id
    )
    return _row(row) if row else None


async def get_active_memory(
    conn: asyncpg.Connection,
    project_id: UUID,
    *,
    limit: int = 50,
    memory_type: str | None = None,
) -> list[MemoryEntry]:
    if memory_type:
        rows = await conn.fetch(
            """
            SELECT * FROM memory_entries
            WHERE project_id = $1 AND active = true AND type = $2
            ORDER BY created_at DESC
            LIMIT $3
            """,
            project_id, memory_type, limit,
        )
    else:
        rows = await conn.fetch(
            """
            SELECT * FROM memory_entries
            WHERE project_id = $1 AND active = true
            ORDER BY created_at DESC
            LIMIT $2
            """,
            project_id, limit,
        )
    return [_row(r) for r in rows]


async def get_all_active_with_embeddings(
    conn: asyncpg.Connection, project_id: UUID
) -> list[MemoryEntry]:
    """Fetch all active entries that have embeddings (for similarity search)."""
    rows = await conn.fetch(
        """
        SELECT * FROM memory_entries
        WHERE project_id = $1 AND active = true AND embedding IS NOT NULL
        ORDER BY created_at DESC
        """,
        project_id,
    )
    return [_row(r) for r in rows]


async def deactivate_memory(
    conn: asyncpg.Connection,
    entry_id: UUID,
    project_id: UUID,
) -> bool:
    """Soft-delete a single entry. Returns True if a row was updated."""
    result = await conn.execute(
        """
        UPDATE memory_entries
        SET active = false
        WHERE id = $1 AND project_id = $2 AND active = true
        """,
        entry_id, project_id,
    )
    return int(result.split()[-1]) > 0


async def deactivate_all_of_type(
    conn: asyncpg.Connection, project_id: UUID, memory_type: str
) -> int:
    """Soft-delete all active entries of a type. Returns the count deactivated."""
    result = await conn.execute(
        """
        UPDATE memory_entries
        SET active = false
        WHERE project_id = $1 AND type = $2 AND active = true
        """,
        project_id, memory_type,
    )
    return int(result.split()[-1])
