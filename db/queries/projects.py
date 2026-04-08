"""Project queries — raw SQL, typed dataclasses."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import asyncpg


@dataclass
class Project:
    id: UUID
    user_id: UUID
    name: str
    description: str | None
    industry: str | None
    mode: str
    design_tokens: dict[str, Any]
    component_registry: dict[str, Any]
    created_at: datetime
    updated_at: datetime


def _row(record: asyncpg.Record) -> Project:
    d = dict(record)
    d["design_tokens"] = json.loads(d["design_tokens"]) if isinstance(d["design_tokens"], str) else (d["design_tokens"] or {})
    d["component_registry"] = json.loads(d["component_registry"]) if isinstance(d["component_registry"], str) else (d["component_registry"] or {})
    return Project(**d)


async def create_project(
    conn: asyncpg.Connection,
    user_id: UUID,
    name: str,
    industry: str | None,
    mode: str = "autonomous",
    description: str | None = None,
) -> Project:
    row = await conn.fetchrow(
        """
        INSERT INTO projects (user_id, name, description, industry, mode)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        user_id, name, description, industry, mode,
    )
    return _row(row)


async def get_project(
    conn: asyncpg.Connection, project_id: UUID, user_id: UUID
) -> Project | None:
    row = await conn.fetchrow(
        "SELECT * FROM projects WHERE id = $1 AND user_id = $2",
        project_id, user_id,
    )
    return _row(row) if row else None


async def get_project_by_id(
    conn: asyncpg.Connection, project_id: UUID
) -> Project | None:
    row = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
    return _row(row) if row else None


async def list_projects(
    conn: asyncpg.Connection, user_id: UUID
) -> list[Project]:
    rows = await conn.fetch(
        "SELECT * FROM projects WHERE user_id = $1 ORDER BY created_at DESC",
        user_id,
    )
    return [_row(r) for r in rows]


async def update_project_mode(
    conn: asyncpg.Connection, project_id: UUID, mode: str
) -> None:
    await conn.execute(
        "UPDATE projects SET mode = $1 WHERE id = $2", mode, project_id
    )


async def update_design_tokens(
    conn: asyncpg.Connection, project_id: UUID, tokens: dict[str, Any]
) -> None:
    await conn.execute(
        "UPDATE projects SET design_tokens = $1::jsonb WHERE id = $2",
        json.dumps(tokens), project_id,
    )


async def update_component_registry(
    conn: asyncpg.Connection, project_id: UUID, registry: dict[str, Any]
) -> None:
    await conn.execute(
        "UPDATE projects SET component_registry = $1::jsonb WHERE id = $2",
        json.dumps(registry), project_id,
    )


async def delete_project(conn: asyncpg.Connection, project_id: UUID) -> None:
    await conn.execute("DELETE FROM projects WHERE id = $1", project_id)
