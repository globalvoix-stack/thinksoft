"""Context bus snapshot queries — raw SQL, typed dataclasses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg


@dataclass
class ContextSnapshot:
    id: UUID
    project_id: UUID
    session_id: UUID
    snapshot: dict[str, Any]
    created_at: datetime


def _row(record: asyncpg.Record) -> ContextSnapshot:
    d = dict(record)
    raw = d.get("snapshot")
    d["snapshot"] = json.loads(raw) if isinstance(raw, str) else (raw or {})
    return ContextSnapshot(**d)


async def save_snapshot(
    conn: asyncpg.Connection,
    project_id: UUID,
    session_id: UUID,
    snapshot: dict[str, Any],
) -> ContextSnapshot:
    row = await conn.fetchrow(
        """
        INSERT INTO context_bus_snapshots (project_id, session_id, snapshot)
        VALUES ($1, $2, $3::jsonb)
        RETURNING *
        """,
        project_id, session_id, json.dumps(snapshot),
    )
    return _row(row)


async def get_latest_snapshot(
    conn: asyncpg.Connection, project_id: UUID, session_id: UUID | None = None
) -> ContextSnapshot | None:
    if session_id:
        row = await conn.fetchrow(
            """
            SELECT * FROM context_bus_snapshots
            WHERE project_id = $1 AND session_id = $2
            ORDER BY created_at DESC LIMIT 1
            """,
            project_id, session_id,
        )
    else:
        row = await conn.fetchrow(
            """
            SELECT * FROM context_bus_snapshots
            WHERE project_id = $1
            ORDER BY created_at DESC LIMIT 1
            """,
            project_id,
        )
    return _row(row) if row else None


async def get_snapshot_by_id(
    conn: asyncpg.Connection, snapshot_id: UUID
) -> ContextSnapshot | None:
    row = await conn.fetchrow(
        "SELECT * FROM context_bus_snapshots WHERE id = $1", snapshot_id
    )
    return _row(row) if row else None


async def list_session_snapshots(
    conn: asyncpg.Connection, project_id: UUID, session_id: UUID
) -> list[ContextSnapshot]:
    rows = await conn.fetch(
        """
        SELECT * FROM context_bus_snapshots
        WHERE project_id = $1 AND session_id = $2
        ORDER BY created_at ASC
        """,
        project_id, session_id,
    )
    return [_row(r) for r in rows]
